# Gallery of Apps

This directory hosts the code to setup the gallery of apps page. To ensure that an app shows in the gallery of apps, you must add them to the [apps.yml file](./_data/apps.yml).

For example, if a new app is added to the root "apps" directory "apps/006_some_new_app/your_app_file.py" this should be added at the end of the [apps.yml file](./_data/apps.yml)

```yml
  - name: Some new App
    repo: 006_some_new_app/your_app_file.py # actual python file that will be in the "apps" directory.
    description: "Some very clear explanation of this new app" # clear and small description about this app and what it does.
    reqs: [plotly, openpyxl] # optional - list of requirements this app needs to work.
    image: 001_template.jpg # optional - preview screenshot of the app.
```

If you don't do this, the app will not show up in the gallery page.


# To test locally
```bash
JEKYLL_VERSION=3.8 \
docker run --rm \
  --volume="$PWD:/srv/jekyll:Z" \
  --volume="$PWD/.vendor/bundle:/usr/local/bundle:Z" \
  -p 4000:4000 \
  -it jekyll/jekyll:$JEKYLL_VERSION \
  jekyll serve
```
