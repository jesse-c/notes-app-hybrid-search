# Get the data

cd ~/src/github.com/threeplanetssoftware/apple_cloud_notes_parser/
mkdir -p data
cp ~/Library/Group\ Containers/group.com.apple.notes/NoteStore.sqlite data/NoteStore.sqlite
bundle install
ruby notes_cloud_ripper.rb -f data/NoteStore.sqlite --individual-files -o output
ruby notes_cloud_ripper.rb -m /Users/jesse/Library/Group\ Containers/group.com.apple.notes/ --individual-files -o output
mv output/{TIMESTAMP}/* ~/src/github.com/jesse-c/notes-app-hybrid-search/data/01-from-notes-app-to-plaintext/input/
cp -r output/2024_12_26-19_24_12 ~/src/github.com/jesse-c/notes-app-hybrid-search/data/01-from-notes-app-to-plaintext/input/
cd ~/src/github.com/jesse-c/notes-app-hybrid-search
xsv sample 5 data/01-from-notes-app-to-plaintext/input/csv/note_store_notes_1.csv
