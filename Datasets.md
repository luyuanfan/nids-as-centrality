[README](README.md) | [Introduction](Introduction.md) | Datasets ⮕ | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2](Task-2.md) | [Notebook](nids-as-centrality.ipynb)

# Datasets

## BGP Routing Table (RIB) Snapshots

In the [BGP assignment](https://github.com/CAIDA/nids-bgp-control-plane), you fetched BGP Routing Information Base (RIB) snapshots from a *single* collector managed by [RouteViews](https://www.routeviews.org/routeviews/). This time, you will fetch the same type of data from *multiple* collectors, managed by [RIPE RIS](https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/). 

We use collectors in Amsterdam (RRC00), São Paolo (RRC15), and Singapore (RRC23). These collectors are geographically diverse and are located at large Internet eXchange Points (IXPs), so they provide a sufficiently (for our purposes) global perspective of the Internet.

Using data from more collectors requires significantly more computing power. When first writing your code, you should use `COLLECTORS = ["rrc06"]` so that the notebook executes more quickly. When answering the questions for the tasks, use the larger set of data with `COLLECTORS = ["rrc00", "rrc15", "rrc23"]`.

| Collector | Location | File size |
|---|---|---|
| `rrc00` | Amsterdam, NL | ~404 MB |
| `rrc06` | Otemachi, JP | ~41 MB |
| `rrc15` | São Paolo, BR | ~137 MB |
| `rrc23` | Singapore, SG | ~81 MB |


## MRT Format and bgpkit

RIB files are stored in **MRT (Multi-Threaded Routing Toolkit)** format.
Each entry represents one prefix announcement and contains:

| Field           | Example      | Description                                                                      |
| --------------- | ------------ | -------------------------------------------------------------------------------- |
| **collector**   | route-views2 | Name of the collector                                                            |
| **peer_asn**    | 10           | The ASN of the vantage point                                                     |
| **peer_ip**     | 12.3.2.1     | The IP address of the vantage point                                              |
| **as_path**     | 10 724 8234  | Sequence of ASNs the route traversed                                             |
| **origin_asns** | 8234         | Last ASN in the path — the AS that originated the prefix. When a prefix is announced by more than one origin AS, it is called a MOAS prefix.                                                             |
| **prefix**      | 43.0.0.0/24  | The announced IP prefix in CIDR notation                                         |


The notebook uses **[bgpkit](https://bgpkit.com/)**, a library for parsing MRT-format BGP data. bgpkit handles decompression, MRT record parsing, and filtering, letting the notebook iterate over RIB entries as Python objects without dealing with the binary format directly.
```python
for elem in bgpkit.Parser(url=url):
    elem.collector
    elem.peer_asn
    (etc)
```

For a more comprehensive documentation of MRT format, you could refer to the 
[bgpkit documentation](https://docs.rs/bgpkit-parser/latest/bgpkit_parser/models/struct.BgpElem.html).

## RIPE AS Names
RIPE maintains a [mapping of ASNs](https://ftp.ripe.net/ripe/asnames/) to their corresponding ASes and organizations.

## CAIDA AS Rank

CAIDA's [AS Rank](https://asrank.caida.org/) project sorts ASes by their customer cone size. The table is generated using the same data from [the BGP Control Plane assignment](https://github.com/CAIDA/nids-bgp-control-plane/).

[README](README.md) | [Introduction](Introduction.md) | Datasets ⮕ | [Tasks](Tasks.md) | [Task 1](Task-1.md) | [Task 2](Task-2.md) | [Notebook](nids-as-centrality.ipynb)
