# Vanta Scripts

## Setup

1. Install [UV](https://docs.astral.sh/uv/guides/install-python/).
2. Create an `.env` file and add the following. If you need to create a new API access token, then follow the
[authentication documentation](https://developer.vanta.com/docs/api-access-setup).
    
    ```bash
   VANTA_CLIENT_ID=your_vanta_client_id
   VANTA_API_TOKEN=your_vanta_api_token
    ```

## Running Scripts

To run a script in the scripts directory use the following syntax:

```bash
uv run scripts/script_name.py
```

For example to run the `remove_pci_controls.py` script. First create a CSV file with the columns `pci_dss_req_num` and
`scope`. Only rows with the value, "Not applicable" in the scope column will be removed.

Example:

| pci_dss_req_num  | scope          |
|------------------|----------------|
| 7.2.5            | Not applicable |
| 7.2.5.1          | Not applicable |
| 7.2.6            | Not applicable |

Then run the script using the following syntax:

    ```bash
    uv run scripts/remove_pci_controls.py path/to/your/file.csv
    ```