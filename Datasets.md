# Datasets

## BGP Routing Table (RIB) Snapshots

Like [the BGP Control Plane assignment](https://github.com/CAIDA/nids-bgp-control-plane/), we employ BGP Routing Information Base (RIB) snapshots. This time, we source the data from RIPE's publicly available [Routing Information Service](https://www.ripe.net). To get a multifaceted view of the Internet, we use collectors in Amsterdam (RRC00), São Paolo (RRC15), and Singapore (RRC23).

### MRT Format

RIB files are stored in **MRT (Multi-Threaded Routing Toolkit)** format.
Each entry represents one prefix announcement and contains:

| Field           | Example      | Description                                                                       |
| --------------- | ------------ | --------------------------------------------------------------------------------- |
| **collector**   | route-views2 | Name of the collector                                                             |
| **peer_asn**    | 10           | The ASN of the vantage point                                                      |
| **peer_ip**     | 12.3.2.1     | The IP address of the vantage point                                               |
| **as_path**     | 10 724 8234  | Sequence of ASNs the route traversed                                              |
| **origin_asns** | 8234         | Last ASN in the path — the AS that originated the prefix                          |
|                 |              | When a prefix is announced by more than one origin AS, it is called a MOAS prefix |
| **prefix**      | 43.0.0.0/24 | The announced IP prefix in CIDR notation                                          |

![AS path example](images/rib-route.png)

### bgpkit

The notebook uses **[bgpkit](https://bgpkit.com/)**, a library for parsing MRT-format BGP data. bgpkit handles decompression, MRT record parsing, and filtering, letting the notebook iterate over RIB entries as Python objects without dealing with the binary format directly.

```python
for elem in bgpkit.Parser(url=url):
    elem.collector
    elem.peer_asn
    (etc)
```

## CAIDA AS Rank

CAIDA's [AS Rank](https://asrank.caida.org/) project sorts ASes by their customer cone size. The table is generated using the same data from [the BGP Control Plane assignment](https://github.com/CAIDA/nids-bgp-control-plane/).
