# kalinovo-bez-elektriny

## Automate updates

1. Setup, for example, hosting & deployment on [vercel.com](https://vercel.com/)
2. Clone this repo & install dependencies
3. Crate a script `deploy_changes.sh` similar to below
   ```bash
   #!/bin/bash
   /path/to/python \
     /path/to/kalinovo-bez-elektriny/src \
     --log-dir-path "/path/to/logs" \
     --log-file-pattern "app.log" && \
   git -C /path/to/kalinovo-bez-elektriny add -u && \
   git -C /path/to/kalinovo-bez-elektriny commit -m "Update data" && \
   git -C /path/to/kalinovo-bez-elektriny push
   ```

4. Schedule the deployment with cron, for example

   ```bash
   0 */12 * * * /usr/bin/bash /path/to/deploy_changes.sh
   ```


## Development

To run the app locally use
```bash
FLASK_APP=src/app flask run --extra-files src/templates/
```

To freeze the page use
```
python3 -m src.freeze
```
