const data = document.currentScript.dataset;
const DEBUG = data.debug;

const DEFAULT_APP_FILES = {
  "patch.py": {
    url: "https://raw.githubusercontent.com/data-to-insight/patch/main/docs/patch.py",
  },
};
const BASE_REQUIREMENTS = ["streamlit_javascript"];

function urlsToObject(urls, prefix = "") {
  return urls.reduce((acc, url) => {
    const fileName = url.split("/").pop();
    acc[`${prefix}${fileName}`] = { url };
    return acc;
  }, {});
}

const loadAppFromUrl = () => {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);

  const files = urlsToObject(urlParams.getAll("file"));
  const pages = urlsToObject(urlParams.getAll("page"), (prefix = "pages/"));

  const requirements = urlParams.getAll("req");
  if (Object.keys(files).length === 0) {
    mountStlite(DEFAULT_APP_FILES, BASE_REQUIREMENTS);
    return;
  }

  mountStlite({ ...files, ...pages }, requirements);
};

const mountStlite = (files, requirements) => {
  console.log(files);
  console.log(requirements);
  const entryPointName = Object.keys(files)[0];
  stlite.mount(
    {
      requirements: requirements, // Packages to install
      entrypoint: entryPointName, // The target file of the `streamlit run` command - use the first file present
      files: files,
    },
    document.getElementById("root")
  );
};

loadAppFromUrl();
