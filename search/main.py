from enum import Enum

import click
import structlog
import tomllib
from sentence_transformers import SentenceTransformer
from vespa.application import Vespa
from vespa.io import VespaQueryResponse

log = structlog.get_logger()


class Strategy(str, Enum):
    BM25 = "bm25"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class Embedder(str, Enum):
    LOCAL = "local"
    HOSTED = "hosted"


log.debug("config", status="loading")
with open("config.toml", "rb") as f:
    config = tomllib.load(f)
log.debug("config", status="loaded")

app = Vespa(url="http://localhost:8080")


@click.group()
def cli():
    pass


@cli.command()
@click.argument("strategy", type=click.Choice([s.value for s in Strategy]))
@click.argument("text")
@click.option("--num-results", default=10, help="Number of results to return")
@click.option(
    "--embedder",
    type=click.Choice([e.value for e in Embedder]),
    default=Embedder.HOSTED,
    help="Where the embedder model is loaded",
)
def query(strategy, text, num_results, embedder):
    strategy = Strategy(strategy)
    embedder = Embedder(embedder)

    log.debug(f"query strategy: {strategy.value}")
    log.debug(f"query text: {text}")
    log.debug(f"number of results: {num_results}")

    match (embedder, strategy):
        case (Embedder.LOCAL, Strategy.SEMANTIC | Strategy.HYBRID):
            log.debug("model", status="loading")
            model = SentenceTransformer(config["model"]["name"])
            log.debug("model", status="loaded")

            body_embedding = model.encode(text).tolist()
            body = {
                "input.query(query_embedding)": body_embedding,
            }
        case (Embedder.HOSTED, Strategy.SEMANTIC | Strategy.HYBRID):
            body = {
                "text": text,
                "input.query(query_embedding)": "embed(@text)",
            }

        case _:
            model = None

    with app.syncio(connections=1) as session:
        match strategy:
            case Strategy.BM25:
                response: VespaQueryResponse = session.query(
                    yql="select * from sources entries where userQuery()",
                    query=text,
                    ranking=strategy.value,
                    hits=num_results,
                )
            case Strategy.SEMANTIC:
                response: VespaQueryResponse = session.query(
                    body=body,
                    yql=(
                        "select * from sources entries where "
                        f"{{targetHits:{num_results}}}"
                        "(nearestNeighbor(body_embedding, query_embedding))"
                    ),
                    ranking="embedding_similarity",
                    hits=num_results,
                )
            case Strategy.HYBRID:
                response: VespaQueryResponse = session.query(
                    body=body,
                    yql=(
                        "select * from sources entries where "
                        f"{{targetHits:{num_results}}}"
                        "(nearestNeighbor(body_embedding, query_embedding))"
                        "or userQuery()"
                    ),
                    query=text,
                    ranking=strategy.value,
                    hits=num_results,
                )

        assert response.is_successful()

        for i, hit in enumerate(response.hits, 1):
            log.debug(
                "hit",
                index=i,
                title=hit["fields"]["title"],
                relevance=f"{hit['relevance']:.4f}",
                snippet=hit["fields"]["body"][:25],
            )


if __name__ == "__main__":
    cli()
