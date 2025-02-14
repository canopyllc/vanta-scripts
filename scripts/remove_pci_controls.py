import csv
import json
import time
import argparse
from functools import lru_cache
from textwrap import dedent

import requests
import logging
from environs import Env

log = logging.getLogger(__name__)
all_controls = []

VANTA_BASE_URL = "https://api.vanta.com/v1"
PCI_FRAMEWORK_ID = "pciDss4"


@lru_cache
def get_auth_token():
    url = "https://api.vanta.com/oauth/token"
    payload = json.dumps(
        {
            "client_id": VANTA_CLIENT_ID,
            "client_secret": VANTA_API_TOKEN,
            "scope": "vanta-api.all:read vanta-api.all:write",
            "grant_type": "client_credentials",
        }
    )
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()["access_token"]


def make_request(url, method, data=None, params=None):
    vanta_api_token = get_auth_token()
    response = getattr(requests, method)(
        f"{VANTA_BASE_URL}/{url}",
        headers={
            "Authorization": f"Bearer {vanta_api_token}",
            "Content-Type": "application/json",
        },
        data=data,
        params=params,
    )
    response.raise_for_status()
    return response


def read_controls_from_csv(filename):
    """Read PCI controls from CSV file."""
    controls = []
    try:
        with open(filename, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["scope"] != "Not applicable":
                    continue
                controls.append(row["pci_dss_req_num"])
        log.info(f"Successfully read {len(controls)} controls from CSV")
        return controls
    except Exception as e:
        log.error(f"Error reading CSV file: {str(e)}")
        raise


def get_all_controls(page_cursor=None):
    """Get all Vanta controls."""
    response = make_request(
        "controls",
        "get",
        params={
            "pageSize": 100,
            "frameworkMatchesAny": "pciDss4",
            "pageCursor": page_cursor,
        },
    )
    response.raise_for_status()
    data = response.json()
    all_controls.extend(data["results"]["data"])
    page_info = data["results"]["pageInfo"]
    end_cursor = page_info["endCursor"]
    has_next_page = page_info["hasNextPage"]
    if has_next_page:
        get_all_controls(end_cursor)
    else:
        return all_controls
    pass


def get_control_id(control_number):
    """Get Vanta control ID for a given PCI DSS requirement number."""
    for control in all_controls:
        if control["name"] == control_number:
            return control["id"]


def remove_control(control_id):
    """Remove a control from Vanta using its ID."""
    try:
        make_request(f"controls/{control_id}", "delete")
        return True
    except requests.exceptions.RequestException as e:
        log.error(f"Error removing control {control_id}: {str(e)}")
        return False


def main(csv_file):
    try:
        # Read controls from CSV
        controls_to_remove = read_controls_from_csv(csv_file)

        # Track statistics
        total = len(controls_to_remove)
        removed = 0
        failed = 0

        # Get all controls
        get_all_controls()

        # Process each control
        for control_number in controls_to_remove:
            log.info(f"Processing control {control_number}")

            # Get control ID
            control_id = get_control_id(control_number)
            if not control_id:
                log.warning(
                    f"Skipping control {control_number} - Could not find control ID"
                )
                failed += 1
                continue

            # Remove control
            if remove_control(control_id):
                log.info(f"Successfully removed control {control_number}")
                removed += 1
            else:
                log.error(f"Failed to remove control {control_number}")
                failed += 1

            # Add a small delay to avoid rate limiting
            time.sleep(0.5)

        # Log summary
        log.info(
            dedent(
                f"""
                Summary:
                Total controls processed: {total}
                Successfully removed: {removed}
                Failed: {failed}
                """
            )
        )

    except Exception as e:
        log.error(f"Script execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    env = Env()
    env.read_env()
    VANTA_CLIENT_ID = env("VANTA_CLIENT_ID")
    VANTA_API_TOKEN = env("VANTA_API_TOKEN")

    # Set up logging
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Remove PCI controls from Vanta.")
    parser.add_argument("csv_file", help="Path to the CSV file containing controls to remove")
    args = parser.parse_args()

    main(args.csv_file)