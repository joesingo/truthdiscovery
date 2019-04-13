# Stock dataset example

This directory contains an example of using truth-discovery on a real-world
dataset. The data is the 'stock' dataset from ["Data Sets for Data Fusion
Experiments"](http://lunadong.com/fusionDataSets.htm), which contains
information about 1,000 stock symbols from 55 sources on each week day in July
2011.

## Data format

The `data` directory inside `data.zip` contains a file for each day in
*tab-separated values* format. Each line in each file lists the values claimed
by a source on a given date for several attributes relating to a stock symbol.
The format in this repo is the same as in the original data, except that the
date has been added as the first column (in `YYYY-MM-DD` format). The columns
are:

* Date
* Source
* Symbol
* Change %
* Last trading price
* Open price
* Change $
* Volume Today's high
* Today's low Previous close
* 52wk High
* 52wk Low
* Shares Outstanding P/E Market cap
* Yield
* Dividend
* EPS

Note that there are no header rows.

Dates were added to each file so that the files can be concatenated to perform
truth-discovery on *all* of the data (warning: may take several minutes). In a
Unix environment one can simply do
```bash
cat data/data-*.tsv > all_data.tsv
```
and run the `stock_dataset.py` script on `all_data.tsv`.

## True values

A gold standard dataset of these attributes for 100 NASDAQ stocks is also
provided in the original data (collected by the original authors from
[nasdaq.com](https://nasdaq.com)). In this repo the files are in the `truth`
directory inside the zip, in the same format as `data` but without the `source`
column. As with the claims data, these files can be concatenated to perform
accuracy calculations using all the available data.

## Experiments

This directory contains a script `stock_dataset.py` which runs each of the
supported algorithms on the stock data, and measures the accuracy with respect
to the NASDAQ truth data.

Values in the source's claims and in the true values are 'cleaned' to account
for differences in formatting by removing any `$`, `%`, `+` or `-` characters,
and removing leading and trailing whitespace.

This script also serves as an example of using the `FileDataset` and
`FileSupervisedData` helper classes.
