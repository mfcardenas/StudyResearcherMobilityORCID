# StudyResearcherMobilityORCID
Using ORCID as a Data Source to Study Researcher Mobility: An Analysis of Germany, France, the Netherlands, Spain, and Italy.

# Additional Documentation

## Data download and extraction
Due to the size of the information to be downloaded, a CPD (Data Processing Center) in a virtual machine and not locally is chosen, suitable for the flexibility and security it offers in the flow of information. In addition, it offers high remote availability to researchers through single non-concurrent access.

For data downloading and processing, a virtual machine hosted in Microsoft Azure is used, equipped with 4 processing cores, 16 GB of RAM, a 2 TB disk of storage, up to 1 TB of network traffic, and remote access by VPN (Virtual Private Network) with Bastion security and monitoring system, and with automated on and off capabilities in a 24/7 operational service.

## ORCID data
Public information about ORCID data is located mainly at two URLs (Uniform Resource Locator):
1. [https://github.com/ORCID/ORCID-Source](https://github.com/ORCID/ORCID-Source)
2. [https://info.orcid.org/es/](https://info.orcid.org/es/)

Use of data in the file is governed by the data file's terms of use (Spanish version) [Terms of Use](https://info.orcid.org/es/pol%C3%ADtica-de-uso-de-archivos-de-datos-p%C3%BAblicos) and the [Privacy Policy](https://info.orcid.org/es/Pol%C3%ADtica-de-Privacidad/). The Public Data Archive is released annually under a dedicated public domain CC0 1.0 developed by Creative Commons with the publication of recommended community standards for its use without restrictions or conditions (including those contained in the Terms and Conditions of Use and Membership Agreement) added.

## ORCID data structure and hierarchy
Below is an outline of the Activities file hierarchy.

![Activity File Hierarchy](https://github.com/mfcardenas/StudyResearcherMobilityORCID/tree/61babd82527ff4aee9929ff361f17819fdc45f65/img/activity-file-hierarchy.png)
*Source: ORCID*

Likewise, below is a diagram of the hierarchy of the Summaries file.

![Summary Archive Hierarchy](https://github.com/mfcardenas/StudyResearcherMobilityORCID/tree/61babd82527ff4aee9929ff361f17819fdc45f65/img/summary-archive-hierarchy.png)
*Source: ORCID*

## Queries and data analysis
PowerBI is used to generate subsample query reports in the virtual machine, which is a unified and scalable data analysis tool from Microsoft that is aimed at interactive data visualization. It has a simple and intuitive interface for any type of end user to create their own reports and dashboards. These types of digital tools are used in the so-called business intelligence (BI), which tries to transform basic information (data) into knowledge to optimize the decision-making process in a company.

The following image shows one of the generated previews.

![Map and table of previous results](https://github.com/mfcardenas/StudyResearcherMobilityORCID/tree/61babd82527ff4aee9929ff361f17819fdc45f65/img/map-table-preview.png)
*Source: own elaboration based on ORCID data*

