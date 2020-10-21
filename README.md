# Bonding Curve Plot
How to Visualize the curation bonding curve for a given subgraph from https://testnet.thegraph.com

if you'd like to learn more here are links to the video where it was first explained and a calculator to play with the variables yourself:
- https://youtu.be/Ia0lt0KRVSg?t=1909
- https://www.desmos.com/calculator/fraz3rqitg


A list of all current subgraph addresses can be found here:
- https://rinkeby.etherscan.io/address/0x513f5ba9d55587552c3fb1cb60411196265e7ff2

If you signalled a subgraph and know the amount of GST you received 
- Go to the tx of the contract interaction
- Click on the Graph Curation Share and use that contract address to visualize the curve 

Some popular ones

| Subgraph        | Address                                    |
|-----------------|--------------------------------------------|
| Uniswap         | 0x130d022e85c74c6bdc40eaa4cf483db4e198a979 |
| Compound        | 0x09a1e9751396155424e5ab56425ada306935dbb4 |
| Balancer        | 0xf69e9eaa6124dad43fb8efdf31b305b7ba64e0d9 |
| Synthetix Rates | 0xf912697b908240a41fc7f87b9004e853709b0a36 |

## Requirements
- python (3.4+)
- beautifulsoup4
- selenium
- matplotlib
- chromedriver

```shell
pip3 install beautifulsoup4
pip3 install selenium
pip3 install matplotlib
wget https://chromedriver.storage.googleapis.com/<version>/chromedriver_linux64.zip # get version number at chrome://version
unzip chromedriver_linux64.zip

# If running from a pipenv
sudo apt-get install python3-tk
```
**Parameters**
```shell
    k=1/3 # Reserve Ratio
    b=tlist["reserves"] #Current reserves under curve
    s=tlist["tokensupply"] # Current GST supply
    n=((1/k)-1) # Function of reserve ratio 
    m=((b*(n+1))/(s**(n+1))) # Shape of curve based off reserves and supply
```

**Run**

```shell
cd ./BondingCurve
./python3 BondingCurvePlot.py -h
```

This should print the available command-line arguments:

```
BondingCurvePlot.py

USAGE:
    BondingCurvePlot.py [OPTIONS]

FLAGS:
    -h, --help       Prints help information

OPTIONS:
    -n, --name <name>                        Name to save subgraph as
    -s, --subgraph <subgraph address>        Subgraph address
    -a, --address <personal address>         Personal wallet address [OPTIONAL]
```

**Example Usage**

```shell
python3 BondingCurvePlot.py -n Compound -s 0x09a1e9751396155424e5ab56425ada306935dbb4

```
