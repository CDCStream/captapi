import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Captapi — Social Media Data API",
    short_name: "Captapi",
    description:
      "One API for structured public data from 29 social, commerce, ad library, and creator platforms.",
    start_url: "/",
    display: "standalone",
    background_color: "#ffffff",
    theme_color: "#2563eb",
    icons: [
      { src: "/logo.png", sizes: "any", type: "image/png" },
    ],
  };
}
