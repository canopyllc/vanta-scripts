## Remove PCI Controls

1. First get add the following to your `.env` file. You can get the Vanta API token from the Vanta API Credentials item in
   1Password in the DevOps vault. If you need to create a new one follow the
   [authentication documentation](https://developer.vanta.com/docs/api-access-setup) directions.
    
    ```bash
   VANTA_CLIENT_ID=your_vanta_client_id
   VANTA_API_TOKEN=your_vanta_api_token
    ```
2. Update the `pci_controls_to_remove.csv` file with the controls you want to remove.
3. Then run the following command to remove the PCI controls:

    ```bash
    uv run remove_pci_controls.py
    ```