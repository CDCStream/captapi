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
  const Icon = LUCIDE[icon] ?? Search;
  return (
    <Icon
      className={cn("shrink-0", colorClass, className)}
      style={{ width: size, height: size }}
      aria-hidden
    />
  );
}
