cd ~/src/github.com/threeplanetssoftware/apple_cloud_notes_parser/
bundle install
ruby notes_cloud_ripper.rb -f data/NoteStore.sqlite --individual-files -o output
mv output/2024_08_18-21_35_59 ~/src/github.com/jesse-c/notes-app-semantic-search/output/
cd ~/src/github.com/jesse-c/notes-app-semantic-search
cat output/2024_08_18-21_35_59/csv/note_store_notes_1.csv
