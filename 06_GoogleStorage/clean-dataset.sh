cat income_data.csv | head -n500 > shortened_income_data.csv
var=`cat shortened_income_data.csv`
echo "${var//;/|}" > shortened_income_data_separated_by_pipes.csv 
cat shortened_income_data_separated_by_pipes.csv | wc -l
