FROM node:10-slim
LABEL maintainer="Imed Eden"

# Installing the latest chrome dev package and fonts to support different charsets
# and installing the necessary libs to make the bundled version of Chromium that Puppeteer
RUN apt-get update \
    && apt-get install -y sudo \
    && apt-get install -y apt-utils \
    && apt-get install -y wget gnupg \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y google-chrome-unstable fonts-ipafont-gothic fonts-wqy-zenhei fonts-thai-tlwg fonts-kacst fonts-freefont-ttf \
    #  --no-install-recommends \
    && apt-get install -y ca-certificates curl apt-transport-https lsb-release gnupg  \
    #  --no-install-recommends \
    && curl -sL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc.gpg > /dev/null \
    && AZ_REPO=$(lsb_release -cs) \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | sudo tee /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update \
    && apt-get install azure-cli \
    && rm -rf /var/lib/apt/lists/*

# Install puppeteer and user
RUN npm i puppeteer \
    # Add user so we don't need --no-sandbox.
    # same layer as npm install to keep re-chowned files from using up several hundred MBs more space
    && groupadd -r pptruser && useradd -r -g pptruser -G audio,video pptruser

#RUN mkdir -p /var/app
WORKDIR /home/pptruser
COPY . .

USER root

CMD ["google-chrome-unstable"]
ENTRYPOINT ["node", "sephora-scrap.js"]
