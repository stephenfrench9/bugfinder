docker build -t testmodel .
export ports=5000
export ings=localhost
/usr/bin/open -a "/Applications/Google Chrome.app" 'http://'$ings:$ports/format?helloTo=rick
docker run -dp 5000:5000 --name goo testmodel
