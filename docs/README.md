# Gallery of Apps

This directory hosts the code to setup the gallery of apps page. To ensure that an app shows in the gallery of apps, you must add them to the [apps.yml file](./_data/apps.yml).

For example, if a new app is added to the root "apps" directory `apps/006_some_new_app/your_app_file.py` this should be added at the end of the [apps.yml file](./_data/apps.yml):

```yml
  - name: Some new App
    repo: 006_some_new_app/your_app_file.py
    description: "Some very clear explanation of this new app"
    reqs: [plotly, openpyxl] # optional
    image: 001_template.jpg # optional
```

where:

| Name| Description |
| - | - |
| name| Name of the app   |
| repo   | path to the python file. It should be in it's own directory within the `apps` directory. [see this example](../apps/000_intro/app.py).|
|description| clear and small description about this app and what it does.|
|reqs| *optional* - list of requirements this app needs to work. Ideally, they should be defined in a `requirements.txt` file within the app's directory (the same as where the python file is) for the app to work in development. However, they must be manually inserted here for the app to work in production. If there's no extra requirements, don't add this field.
|image| *optional* - app's preview/screenshot image. the images should live in the directory [`docs/img/app_previews`](./img/app_previews/) so that it's accessible through the jekyll website. If there's no image, don't add this field.




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
