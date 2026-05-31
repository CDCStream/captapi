import Image from "next/image";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/30 p-4">
      <Link href="/" className="flex items-center gap-2 mb-8">
        <Image
          src="/logo.png"
          alt="Captapi"
          width={28}
          height={28}
          className="size-7 rounded-md"
          priority
        />
        <span className="brand-wordmark text-xl">
          Capt<span className="gradient-text">api</span>
        </span>
      </Link>
      {children}
      <Link
        href="/"
        className="mt-6 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Back to home
      </Link>
    </div>
  );
}
