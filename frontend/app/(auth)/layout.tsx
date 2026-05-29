import Link from "next/link";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-muted/30 p-4">
      <Link href="/" className="flex items-center gap-2 mb-8">
        <div className="size-7 rounded-md bg-primary" />
        <span className="font-bold text-lg">Captapi</span>
      </Link>
      {children}
    </div>
  );
}
