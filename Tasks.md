[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | Tasks ⮕ | [Task 1](Task-1.md) | [Task 2](Task-2.md) | [Notebook](nids-as-centrality.ipynb)


# Tasks

Complete the tasks below in order. All tasks should be completed in the Jupyter Notebook

---

### Task 0: Setup
There are multiple options for how to run this notebook

- Access NRP's JupyterHub: https://jupyterhub-west.nrp-nautilus.io
  - Detailed access instructions: [How to access NRP](https://www.caida.org/projects/nids/how-to/access-nrp/)
  - When spawning your server, select the SciPy image/profile

- Run locally
  - Clone the repo and run the notebook in VS Code or other prefered software

- Run using GitHub codespaces
  - Click the green code button on the repo (where you normally go for cloning)
  - Click Codespaces and start Codespace

### Task 1: Calculate Betweenness Centrality

Detailed Guidance &rarr; [Task-1 Guide](Task-1.md)

- Complete the YOUR CODE HERE segments
- Answer all questions in the notebook

Q1: What does betweenness centrality measure?

Q2: Why would we use the weighted betweenness centrality versus the unweighted betweenness centrality?

Q3: What are the top 5 ASes ranked by their weighted betweenness centralities? How these compare to the top ASes [as ranked by customer cone size](https://asrank.caida.org/)? Does this make sense? Why?

Q4: What shape does the CCDF have? What does this tell us about the distribution of weighted betweenness centralities?

### Task 2: Hegemony

Detailed Guidance &rarr; [Task-2 Guide](Task-2.md)

- Complete the YOUR CODE HERE segments
- Answer all questions in the notebook

Q1: Why do we remove the top and bottom $\alpha$ proportions of the viewpoints?

Q2: How do the top 5 ASes ranked by betweenness centrality compare to the top 5 ranked by AS hegemony?

Q3: What does the concentration of points on the $x = y$ line tell us about the relationship between betweenness centrality and AS hegemony?

Q4: Look up the AS that corresponds to the outlier point. How does this AS's geographic location relate to the location of the collectors?

Q5: Why does the geographic location of the outlier AS cause its betweenness centrality to be so much larger than its AS hegemony?

[README](README.md) | [Introduction](Introduction.md) | [Datasets](Datasets.md) | Tasks ⮕ | [Task 1](Task-1.md) | [Task 2](Task-2.md) | [Notebook](nids-as-centrality.ipynb)
