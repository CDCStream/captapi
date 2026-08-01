import type { ReactElement } from "react";
import Image from "next/image";
import {
  Youtube,
  AtSign,
  Cloud,
  Music2,
  Instagram,
  Facebook,
  Github,
  Linkedin,
  Megaphone,
  MessagesSquare,
  Pin,
  ShoppingBag,
  Calendar,
  Twitter,
  Video,
  Search,
  LinkIcon,
  Ghost,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

const LUCIDE: Record<string, LucideIcon> = {
  youtube: Youtube,
  music: Music2,
  instagram: Instagram,
  facebook: Facebook,
  twitter: Twitter,
  reddit: MessagesSquare,
  threads: AtSign,
  bluesky: Cloud,
  pinterest: Pin,
  linkedin: Linkedin,
  rumble: Video,
  github: Github,
  megaphone: Megaphone,
  shoppingBag: ShoppingBag,
  calendar: Calendar,
  video: Video,
  cloud: Cloud,
  search: Search,
  link: LinkIcon,
  ghost: Ghost,
};

type BrandProps = { size: number; className?: string };

/** Simple Icons–style brand marks (currentColor unless multicolor). */
function TikTokMark({ size, className }: BrandProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={cn("shrink-0", className)}
      fill="currentColor"
      aria-hidden
    >
      <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z" />
    </svg>
  );
}

function GoogleMark({ size, className }: BrandProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={cn("shrink-0", className)}
      aria-hidden
    >
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.76h3.56c2.08-1.92 3.28-4.74 3.28-8.09Z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.56-2.76c-.98.66-2.23 1.06-3.72 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84A11 11 0 0 0 12 23Z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.11a6.6 6.6 0 0 1 0-4.22V7.05H2.18a11 11 0 0 0 0 9.9l3.66-2.84Z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.65l3.15-3.15C17.45 2.09 14.97 1 12 1A11 11 0 0 0 2.18 7.05l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38Z"
      />
    </svg>
  );
}

function AmazonMark({ size, className }: BrandProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={cn("shrink-0", className)}
      fill="currentColor"
      aria-hidden
    >
      <path d="M13.958 10.09c0 1.232.029 2.256-.591 3.351-.502.891-1.301 1.439-2.186 1.439-1.214 0-1.922-.924-1.922-2.292 0-2.692 2.415-3.182 4.7-3.182v.684zm3.186 7.705c-.209.189-.512.201-.745.074-1.115-.926-1.314-1.356-1.927-2.24-1.85 1.886-3.156 2.449-5.554 2.449-2.833 0-5.041-1.746-5.041-5.239 0-2.723 1.861-4.581 4.503-4.581 1.316 0 2.409.274 3.282.742V7.414c0-1.43.041-3.118-1.136-4.229-.915-.887-2.436-.629-3.047-.312-.212.11-.435.26-.6.4-.185.15-.3.18-.505.068l-1.816-.953c-.212-.111-.29-.348-.174-.546.348-.59 1.001-1.085 1.773-1.45C6.8.24 7.993 0 9.346 0c1.696 0 3.11.46 3.95 1.402 1.085 1.191.981 2.778.981 4.507v7.749c0 .925.383 1.332.744 1.822.127.172.156.378-.007.518-.41.347-1.146.986-1.552 1.347-.144.13-.334.14-.487.004zm4.432 1.865c-2.601 1.922-6.375 2.944-9.622 2.944-4.552 0-8.649-1.683-11.745-4.481-.243-.22-.026-.521.266-.35 3.349 1.947 7.491 3.117 11.766 3.117 2.886 0 6.058-.598 8.98-1.836.441-.187.81.29.355.606zm1.534-1.61c-.333-.427-2.205-.202-3.048-.101-.255.03-.294-.191-.064-.351 1.498-1.053 3.959-.75 4.247-.397.289.354-.076 2.809-1.482 3.979-.216.18-.421.084-.325-.153.315-.783 1.023-2.546.672-2.977z" />
    </svg>
  );
}

const BRAND: Record<string, (p: BrandProps) => ReactElement> = {
  tiktok: TikTokMark,
  google: GoogleMark,
  amazon: AmazonMark,
};

/** Platform / group glyph — CaptAPI Account uses the brand logo. */
export function PlatformGlyph({
  icon,
  className,
  colorClass,
  size = 28,
}: {
  icon: string;
  className?: string;
  colorClass?: string;
  size?: number;
}) {
  if (icon === "captapi") {
    return (
      <Image
        src="/logo.png"
        alt="CaptAPI"
        width={size}
        height={size}
        className={cn("shrink-0 rounded-md object-contain", className)}
      />
    );
  }

  const Brand = BRAND[icon];
  if (Brand) {
    // Google is multicolor — ignore colorClass so fills stay brand-correct.
    return (
      <Brand
        size={size}
        className={cn(icon === "google" ? undefined : colorClass, className)}
      />
    );
  }

  const Icon = LUCIDE[icon] ?? Search;
  return (
    <Icon
      className={cn("shrink-0", colorClass, className)}
      style={{ width: size, height: size }}
      aria-hidden
    />
  );
}
