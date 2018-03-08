# mediaReports.py
Provides a way to download media reports

## Local Install (OR) Dependent packages
* Python 3+
* pip3 install edgegrid-python
* pip3 install configparser
* pip3 install requests
* pip3 install logging
* pip3 install timeit
* pip3 install xlsxwriter
* pip3 install csv

### Credentials
In order to use this module, you need to:
* Set up your credential files as described in the [authorization](https://developer.akamai.com/introduction/Prov_Creds.html) and [credentials](https://developer.akamai.com/introduction/Conf_Client.html) sections of the Get Started pagegetting started guide on developer.akamai.comthe developer portal.  
* When working through this process you need to have credentials stored under ~/.edgerc.  The section in your configuration file should be called **'default'**.

### report
Generates a report of download delivery data, based on CPCODES, metrics, dimensions and date.

Sample Command:
```bash
%  python3 media.py -report -cpcodes 586523 -dimensions 2 -metrics 4,21,20,18,28,29,103,113,165,16 -startDate 02/20/2018:20:30 -endDate 02/20/2018:20:45 -format json
```

```

The flags of interest for report are:

```
-cpcodes <cpcode>  Common name to be used to update the certificate/enrollment information in CPS.
-dimensions <dimensions> Comma seperated list of CPCODES
-metrics <metrics> Comma seperated list of metrics
-startDate <Date> Start Date in format MM/DD/YYYY:HH:MM  (Time is in 24 hr format)
-endDate <Date> End Date in format MM/DD/YYYY:HH:MM  (Time is in 24 hr format)
-format <xlsx/json> Output format. Valid values are xlsx (OR) json
  
```


