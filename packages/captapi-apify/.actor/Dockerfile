FROM apify/actor-node:20

# Install dependencies first (better layer caching).
COPY package*.json ./
RUN npm --quiet set progress=false \
 && npm install --omit=dev --omit=optional \
 && echo "Installed npm packages:" \
 && (npm list --omit=dev --all || true) \
 && echo "Node.js version:" && node --version \
 && echo "npm version:" && npm --version

# Copy the rest of the source.
COPY . ./

CMD ["npm", "start", "--silent"]
