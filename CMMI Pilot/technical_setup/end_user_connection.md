## Connecting to the EC2 instance and IDR Cloud
This documentation provides options regarding how to connect to the necessary computing environment, connect to the data in that environment, and the requisite job codes

**The follow job codes are needed to access the AWS EC2 instance and CMS Github:** 
* CMS_CLOUD_ACCESS  
* GITHUB_EDITOR  

**Connecting to the EC2 Instance**
* Option 1: Use the AWS console (available at [CMS CloudTamer](https://cloudtamer.cms.gov/portal)) to connect to the EC2 instance via a web-based interface
* Option 2: Connect to the EC2 instance via an SSH client
    - Collect the Private IP of the instance by navigating to 'instance summary details' in AWS and copy the Private IPv4 address 
    - Locate and download the Private Key file located in S3  (a .pem file) 
    - Connect to the EC2 instance using the Private IP and Private Key  
    
**Connecting to the IDR Cloud through a python-based login**

```
    con = snowflake.connector.connect(
        user= 'abcd',
        password= '*****',
        account= 'cms-idr.privatelink',
    )
 ```

**IDR Cloud Snowflake job codes** 
* The AI Explorer project leveraged CMS claims data available via the Snowflake job codes below. Future projects that model Medicare beneficiary outcomes can consider applying for these job codes to obtain basic data access:

| Job Code                | Description                                                                                               |
| ----------------------  | --------------------------------------------------------------------------------------------------------  |
| IDRSF_VDM_MDCR_P        | Access to Medicare VDM, MDCR Access Layer VDM and MDCR Access Reference VDM in IDRC Snowflake Production  |
| IDRSF_DATA_MDCR_AB_P    | Medicare NCH Part A&B Claim data                                                                          |
| IDRSF_DATA_MMR_P        | Monthly Membership Report/Adjusted Monthly Membership Report (MMR/AMMR) data                              |
| IDRSF_DATA_MDCR_D_P     | Unlimited Medicare Part D Claim data                                                                      |
| IDRSF_DATA_RASRAPS_P    | RAS/RAPS data                                                                                             |
| IDRSF_DATA_RSKSCR_P     | Initial/Mid-Year Risk Scores data                                                                         |
| IDRSF_DATA_PRVDR_PVT_P  | Provider Enumeration Private data (PII/PHI columns)                                                       |
