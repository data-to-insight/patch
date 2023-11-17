# Gallery of Apps

This directory hosts the code to setup the gallery of apps page. To ensure that an app shows in the gallery of apps, you must add them to the [apps.yml file](./_data/apps.yml). For that, you need to create a url for the app first:

- go to https://patch.datatoinsight.org/app and paste the url to the apps github directory, for example https://github.com/data-to-insight/patch/tree/main/apps/000_intro.
- choose the relevant files you want to include. it will generate something like https://patch.datatoinsight.org/app?file=https://raw.githubusercontent.com/data-to-insight/patch/main/apps/000_intro/app.py - this is the url where the will be rendered.
- copy the url.
- At the end of the [apps.yml file](./_data/apps.yml) add a new app:

```yml
  - name: Some new App
    url: https://patch.datatoinsight.org/app?file=https://raw.githubusercontent.com/data-to-insight/patch/main/apps/000_intro/app.py
    description: "Some very clear explanation of this new app"
    image: 001_template.jpg # optional
```

where:

| Name| Description |
| - | - |
| name| Name of the app   |
| url   | app url (generated automatically)|
|description| clear and small description about this app and what it does.|
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
