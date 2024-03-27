## Python Project to scrape Job Postings from LinkedIn and extract specific Details from the Response data object.

import os
import requests
from typing import List
from bs4 import BeautifulSoup
import pandas as pd


class JobPostings:
    """Class Structure to house field data and scrape Job Postings from LinkedIn."""

    def __init__(self, job_title: str, job_search_location: str, start_page: int):
        self.job_title = job_title
        self.job_search_location = (job_search_location,)
        self.search_start_page = start_page
        self.all_posting_page_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={self.job_title}&location={self.job_search_location}&start={self.search_start_page}"
        self.JOB_POST_URL = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/"

    def get_response(self) -> requests.models.Response:
        """Initiates a connection to the LinkedIn Job Posts Page and fetches raw data.

        Returns:
            requests.models.Response: Response type data object from Python Requests library
        """
        response = requests.get(self.all_posting_page_url)
        return response

    def get_job_ids(self, response_data: requests.models.Response) -> List:
        """Parses the response data object and returns a list of Job-Post-specific IDs

        Args:
            response_data (requests.models.Response): Job-page Response data object

        Returns:
            List: List of scraped Job IDs from LinkedIn Response Object
        """
        job_ids = []
        job_list_soup = BeautifulSoup(response_data.text, "html.parser")
        job_data = job_list_soup.find_all("li")
        for each_job_post in job_data:
            base_card_div = each_job_post.find("div", {"class": "base-card"})
            job_id = base_card_div.get("data-entity-urn").split(":")[3]
            job_ids.append(str(job_id))
        return job_ids

    def get_job_title_data(self, job_dict: dict, scraped_data: BeautifulSoup) -> dict:
        """Parses through scraped BeautifulSoup data object and stores Job Title Data in
        job dictionary object.

        Args:
            job (dict): Data structure housing scraped job data
            scraped_data (BeautifulSoup): BeautifulSoup data object housing raw scraped
                data.

        Returns:
            dict: Data Structure housing scraped job data - updated with Job Title data.
        """
        CLASS_LOCATOR = "top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"
        try:
            job_dict["job_title"] = scraped_data.find(
                "h2", {"class": CLASS_LOCATOR}
            ).text.strip()
        except:
            job_dict["job_title"] = None
        return job_dict

    def get_company_data(self, job_dict: dict, scraped_data: BeautifulSoup) -> dict:
        """Parses through scraped BeautifulSoup data object and stores Company Data into
        job dictionary object.

        Args:
            job_dict (dict): Data structure housing scraped job data
            scraped_data (BeautifulSoup): BeautifulSoup data object housing raw scraped
                data.

        Returns:
            dict: Data Structure housing scraped job data - updated with Company Data.
        """
        CLASS_LOCATOR = "topcard__org-name-link topcard__flavor--black-link"
        try:
            job_dict["company_name"] = scraped_data.find(
                "a", {"class": CLASS_LOCATOR}
            ).text.strip()
        except:
            job_dict["company_name"] = None
        return job_dict

    def get_applicant_data(self, job_dict: dict, scraped_data: BeautifulSoup) -> dict:
        """Parses through scraped BeautifulSoup data object and stores Applicant Data
        into job dictionary object.

        Args:
            job_dict (dict): Data structure housing scraped job data
            scraped_data (BeautifulSoup): BeautifulSoup data object housing raw scraped
                data.

        Returns:
            dict: Data Structure housing scraped job data - updated with Applicant Data.
        """
        CLASS_LOCATOR = (
            "num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet"
        )

        try:
            job_dict["number_applicants"] = scraped_data.find(
                "span", {"class": CLASS_LOCATOR}
            ).text.strip()
        except:
            job_dict["number_applicants"] = None
        return job_dict

    def get_time_posted_data(self, job_dict: dict, scraped_data: BeautifulSoup) -> dict:
        """Parses through scraped BeautifulSoup data object and stores Time posted Data
        into job dictionary object.

        Args:
            job_dict (dict): Data structure housing scraped job data
            scraped_data (BeautifulSoup): BeautifulSoup data object housing raw scraped
                data.

        Returns:
            dict: Data Structure housing scraped job data - updated with Time posted Data.
        """
        CLASS_LOCATOR = "posted-time-ago__text topcard__flavor--metadata"
        try:
            job_dict["time_posted"] = scraped_data.find(
                "span", {"class": CLASS_LOCATOR}
            ).text.strip()
        except:
            job_dict["time_posted"] = None
        return job_dict

    def generate_job_data_dict(self, scraped_data: BeautifulSoup, job_id: str) -> dict:
        """Creates structured dictionary containing job post data from scraped
        BeautifulSoup data object.

        Args:
            scraped_data (BeautifulSoup): BeautifulSoup data object housing raw scraped
                data.
            job_id (str): Job ID from the scraped web posting

        Returns:
            dict: Data Structure housing scraped job data - compiled
        """
        job_post_data = {}
        job_post_data["Job_ID"] = job_id
        job_post_data = self.get_job_title_data(job_post_data, scraped_data)
        job_post_data = self.get_company_data(job_post_data, scraped_data)
        job_post_data = self.get_time_posted_data(job_post_data, scraped_data)
        job_post_data = self.get_applicant_data(job_post_data, scraped_data)
        return job_post_data

    def scrape_job_posts(self, job_id_list: List[str]) -> List[dict]:
        """Scrapes LinkedIn using Job IDs as url keys, extracts data and stores it.

        Args:
            job_id_list (List[str]): List of Job-Specific Post IDs used to scrape matches.

        Returns:
            List[dict]: List of Job-Specific data dictionaries containing scraped data.
        """

        list_of_jobs = []
        for _id in job_id_list:
            job_post_url = f"{self.JOB_POST_URL}{_id}"
            response = requests.get(job_post_url)
            scraped_data = BeautifulSoup(response.text, "html.parser")
            job_post_datadict = self.generate_job_data_dict(scraped_data, _id)
            list_of_jobs.append(job_post_datadict)
        return list_of_jobs


def create_dataframe(scraped_data: List[dict]) -> pd.DataFrame:
    """Creates a DataFrame object from a list of dictionaries.

    Args:
        scraped_data (List[dict]): List of dictionaries containing scraped field data
            from LinkedIn.

    Returns:
        pd.DataFrame: DataFrame object.
    """
    constructed_df = pd.DataFrame.from_dict(scraped_data)
    return constructed_df


def export_to_csv(dataframe: pd.DataFrame) -> None:
    """Exports the constructed dataframe to CSV format and saves it to the desired
    directory.

    Args:
        dataframe (pd.DataFrame): Dataframe containing scraped Linkedin Field Data.
    """
    download_dir_path = "/Users/ryearwood/Downloads"
    filename = "Scraped_LinkedIn_Jobposts.csv"
    dataframe.to_csv(os.path.join(download_dir_path, filename), index=False, mode="a")


if __name__ == "__main__":

    job_title = "Python%20Developer"
    job_search_location = "Vancouver%2C%2BBritish%2BColumbia%2C%2BCanada"
    start_page = 0

    linkedin_scraper = JobPostings(job_title, job_search_location, start_page)

    response_data = linkedin_scraper.get_response()
    job_ids = linkedin_scraper.get_job_ids(response_data)
    scraped_job_list = linkedin_scraper.scrape_job_posts(job_ids)
    jobs_df = create_dataframe(scraped_job_list)
    export_to_csv(jobs_df)
