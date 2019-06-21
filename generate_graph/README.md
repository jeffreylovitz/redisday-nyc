# Building a graph from Stack exchange inputs
- Install Python prerequisites with:
`pip3 install --user -r requirements.txt`

- Download the dataset you wish to work with from [https://archive.org/details/stackexchange](https://archive.org/details/stackexchange) and extract the files into the `xml_inputs` directory.

- Run `python3 parse.py` to convert the XML files to a CSV format compatible with the [RedisGraph bulk loader](https://github.com/RedisLabsModules/redisgraph-bulk-loader).

- Populate the graph with:
`python3 bulk_insert.py [graphname] -s -q -n csv_files/User.csv -n csv_files/Question.csv -n csv_files/Tag.csv -n csv_files/Answer.csv -r csv_files/ANSWER_TO.csv -r csv_files/AUTHOR_OF.csv -r csv_files/HAS_TAG.csv`
