## Confluence CLI
A CLI for executing basic operations of Confluence remotely.

### How to run
1. Install pip by following this [guide](https://pip.pypa.io/en/latest/installing.html#install-pip):

2. Install python dependencies:

   ```
   pip install requests[security]
   ```

3. Update Confluence endpoint and space name in client.py:

   ```
   endpoint = 'https://cwiki.apache.org/confluence'
   space = 'STRATOS'
   ```

4. Execute client:
   ```
   python client.py
   
   -------------------------------------------------
   Confluence Client Menu
   -------------------------------------------------
   1: Find Pages Recursively
   2: Find and Replace Page Titles
   3: Find and Replace Text
   4: Exit
   -------------------------------------------------
   
   Select a menu item: 1
   
   ------------------------------
   Find Pages Recursively
   ------------------------------
   Enter page title: 4.1.0 Features
   
   Found page: 4.1.0 Features
   Found page: 4.1.0 Composite Applications
   Found page: 4.1.0 Smart Policies
   Found page: 4.1.0 Cartridge
   Found page: 4.1.0 Apache Stratos Mock IaaS
   Found page: 4.1.0 Persistence Volume Mapping
   Found page: 4.1.0 CLI Tool
   Found page: 4.1.0 Cloud Partitioning
   Found page: 4.1.0 Logging
   Found page: 4.1.0 Load Balancer Extensions
   Found page: 4.1.0 LVS Load Balancer
   Found page: 4.1.0 Setting Up the LVS Load Balancer
   Found page: 4.1.0 Testing the LVS Load Balancer on OpenStack
   Found page: 4.1.0 Troubleshooting Tips for LVS Load Balancer
   
   -------------------------------------------------
   Find and Replace Text
   -------------------------------------------------
   Enter page title: Temp
   Find text: _PAGE4_
   Replace with: page

   Updating page 'Temp'...
   Page 'Temp' updated successfully: [_PAGE4_] -> [page]
   ```
