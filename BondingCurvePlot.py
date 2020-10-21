import sys, getopt
import dataextractor as dex
import matplotlib.pyplot as plt
import numpy as np


def plotpoints(tlist, title):
    """
    Parameters
    ----------
    tlist : list
        list of transactions made
    title: string
        Name of subgraph
    """
    
    k=1/3
    b=tlist["reserves"]
    s=tlist["tokensupply"]
    n=((1/k)-1)
    m=((b*(n+1))/(s**(n+1)))
    x = np.linspace(0,tlist["highestsupply"],100)
    curve = m*(x**n)
    plt.plot(x, curve, 'g-', x, curve*0.95, 'r-')

    txn_buy = np.array(tlist["txn_buy"])  # Token Supply @ Purchase
    price_buy = m*(txn_buy**n)

    txn_sell = np.array(tlist["txn_sell"])  # Token Supply @ Sell
    price_sell = (m*(txn_sell**n))*0.95

    your_txn_buy = np.array(tlist["your_txn_buy"])  # Token Supply @ Purchase
    your_price_buy = (m*(your_txn_buy**n))
    
    your_txn_sell = np.array(tlist["your_txn_sell"])  # Token Supply @ Sell
    your_price_sell = (m*(your_txn_sell**n))*0.95

    plt.plot(txn_buy, price_buy, 'go', txn_sell, price_sell, 'ro')  # plots buys as green sells as red
    if len(your_txn_buy) > 0:
        plt.plot(your_txn_buy, your_price_buy, 'bo', your_txn_sell, your_price_sell, 'yo')  # plots buys as blue sells as yellow
        plt.legend(('Buy Curve', "Sell Curve", 'Buys', "Sells", "Your Buys", "Your Sells"), bbox_to_anchor=(1.05, 1))
    else:
        plt.legend(('Buy Curve', "Sell Curve", 'Buys', "Sells"), bbox_to_anchor=(1.05, 1))
    plt.axvline(s, color='black', linestyle=":")  # plots dotted line at current token supply
    plt.ylabel("Price GRT/GST")
    plt.xlabel("Token Supply")

    
    plt.title(title)
    plt.tight_layout()
    plt.show()


def main(argv):
    project_name = ''
    subgraph_address = ''
    personal_address = ''
    try:
        opts, args = getopt.getopt(argv,"hn:s:a:",["name=","subgraph=","address="])
    except getopt.GetoptError:
        print ('BondingCurvePlot.py\n')
        print('USAGE:')
        print('    BondingCurvePlot.py [OPTIONS]\n')
        print('FLAGS:')
        print('    -h, --help       Prints help information\n')
        print('OPTIONS:')
        print('    -n, --name <name>                        Name of subgraph')
        print('    -s, --subgraph <subgraph address>        Subgraph address')
        print('    -a, --address <personal address>         Personal wallet address')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print ('BondingCurvePlot.py\n')
            print('USAGE:')
            print('    BondingCurvePlot.py [OPTIONS]\n')
            print('FLAGS:')
            print('    -h, --help       Prints help information\n')
            print('OPTIONS:')
            print('    -n, --name <name>                        Name to save subgraph as')
            print('    -s, --subgraph <subgraph address>        Subgraph address')
            print('    -a, --address <personal address>         Personal wallet address [OPTIONAL]')
            sys.exit()
        elif opt in ("-n", "--name"):
            project_name = arg
        elif opt in ("-s", "--subgraph"):
            subgraph_address = arg
        elif opt in ("-a", "--address"):
            personal_address = arg
    transactions = dex.store_transactions(project_name, subgraph_address)
    plotpoints(dex.prepared_transactions(transactions,personal_address), project_name)


if __name__ == "__main__":
    main(sys.argv[1:])
    
