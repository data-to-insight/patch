import json
from urllib.parse import urlparse

import streamlit as st
from pyodide.http import open_url
from streamlit_javascript import st_javascript

st.title("Share PATCh apps")

BASE_URL = "https://patch.datatoinsight.org/app/"
SAVED_APPS_KEY = "saved_apps"


def get_from_local_storage(k):
    v = st_javascript(f"JSON.parse(localStorage.getItem('{k}'));")
    return v or {}


def set_to_local_storage(k, v):
    jdata = json.dumps(v)
    st_javascript(f"localStorage.setItem('{k}', JSON.stringify({jdata}));")


saved_apps = get_from_local_storage(SAVED_APPS_KEY)

if saved_apps:
    st.header("Open a previously used stlite app")
    for app in saved_apps.values():
        path_segments = urlparse(app["search_url"]).path.split("/")
        st.markdown(
            f"""
            - `{app['entrypoint_filename']}` from `{app['search_url']}`
            [launch app]({app['url']}) ↗️
            """,
            unsafe_allow_html=True,
        )

st.header("Search for your PATCh apps")

st.write(
    """
- paste the url to a github folder that contains your files ( for example `https://github.com/data-to-insight/patch/blob/main/apps/000_intro`). 
- It can include both `python` and `requirements.txt` files.
- You can also paste an url that points to just the app's python file (for example `https://github.com/data-to-insight/patch/blob/main/apps/000_intro/app.py`).
"""
)


class Page:
    def __init__(self) -> None:
        self.search_url = None
        self.files = {}
        self.other_files = []

        self.requirements_file = None
        self.include_requirements = True
        self.entrypoint_filename = None

        self.app_url = None

    @property
    def entrypoint_file(self):
        if self.entrypoint_filename and self.files:
            return self.files[self.entrypoint_filename]
        return None

    def build(self):
        self.search_url = st.text_input(
            "github url:",
            placeholder="https://github.com/data-to-insight/patch/blob/main/apps/000_intro",
        )
        if self.search_url:
            self.get_files()
            if self.files:
                self.build_form()
            else:
                st.warning("It is not possible to detect any python files!", icon="⚠️")

    def get_files(self):
        path_segments = urlparse(self.search_url).path.split("/")
        user = path_segments[1]
        repo = path_segments[2]
        directory_path_segments = path_segments[5:]
        inner_directory_path = "/".join(directory_path_segments)

        api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{inner_directory_path}"
        data = open_url(api_url)
        content = json.loads(data.read())

        files = {}
        requirements_file = None
        if isinstance(content, dict):
            content_type = content.get("type", None)
            content_name = content.get("name", None)
            if content_type == "file" and content_name.endswith(".py"):
                files[content_name] = content
            else:
                return
        else:
            for item in content:
                item_type = item.get("type", None)
                item_name = item.get("name", None)
                if item_type == "file" and item_name.endswith(".py"):
                    files[item_name] = item
                elif item_type == "file" and item_name == "requirements.txt":
                    requirements_file = item
                elif item_type == "dir" and item_name == "pages":
                    pages = self.get_pages(item, api_url)
                    files.update(pages)

        self.files = files
        self.requirements_file = requirements_file

    def get_pages(self, item: dict, base_url):
        pages_name = item["name"]
        pages_url = f"{base_url}/{pages_name}"
        data = open_url(pages_url)
        content = json.loads(data.read())
        pages = {}

        if isinstance(content, dict):
            content_type = content.get("type", None)
            content_name = content.get("name", None)
            if content_type == "file" and content_name.endswith(".py"):
                content["is_page"] = True
                pages[f"{pages_name}/{content_name}"] = content
            else:
                return
        else:
            for item in content:
                item_type = item.get("type", None)
                item_name = item.get("name", None)
                if item_type == "file" and item_name.endswith(".py"):
                    item["is_page"] = True
                    pages[f"{pages_name}/{item_name}"] = item
        return pages

    def build_form(self):
        st.header("1 - Entrypoint")

        self.entrypoint_filename = st.radio(
            "Choose your app's entrypoint file 👇",
            options=self.files,
        )

        st.markdown("#")
        st.header("2 - Requirements")
        if self.requirements_file:
            st.write(
                'We found a "requirements.txt" in your directory. Do you want to include it?'
            )
            self.include_requirements = st.checkbox(
                'include "requirements.txt"', value=self.requirements_file is not None
            )
        else:
            st.warning(
                'It is not possible to detect a "requirements.txt" file. If this is not expected, ensure your url points to a directory and not a file.',
                icon="⚠️",
            )

        if len(self.files) > 1:
            other_filenames = [f for f in self.files if f != self.entrypoint_filename]
            st.header("3 - Other files")
            st.write(
                "We found other files in this directory. Which ones should we include?"
            )
            selected_other_filenames = st.multiselect(
                "select files you want to include", other_filenames, other_filenames
            )
            self.other_files = [self.files[f] for f in selected_other_filenames]
        st.markdown("#")

        self.build_app_url()
        self.save_app()

        st.header("3 - Launch your app")
        st.write("Here's your app url. Click on it or copy it to share it.")
        st.write(self.app_url)

    def build_app_url(self):
        url = f'?file={self.entrypoint_file["download_url"]}'

        if self.other_files:
            pages_urls = [
                f["download_url"] for f in self.other_files if f.get("is_page", False)
            ]
            files_urls = [
                f["download_url"]
                for f in self.other_files
                if not f.get("is_page", False)
            ]
            if files_urls:
                url = f"{url}&file={'&file='.join(files_urls)}"
            if pages_urls:
                url = f"{url}&page={'&page='.join(pages_urls)}"

        if self.include_requirements and self.requirements_file:
            data = open_url(self.requirements_file["download_url"])
            requirements = [str(r).strip() for r in data.read().split()]
            url = f"{url}&req={'&req='.join(requirements)}"

        self.app_url = f"{BASE_URL}{url}"

    def save_app(self):
        if self.app_url:
            saved_apps[self.search_url] = {
                "url": self.app_url,
                "search_url": self.search_url,
                "entrypoint_filename": self.entrypoint_filename,
            }
        set_to_local_storage(SAVED_APPS_KEY, saved_apps)


Page().build()
