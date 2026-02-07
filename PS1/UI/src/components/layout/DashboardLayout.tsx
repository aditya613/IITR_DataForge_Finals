import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { Bell, Search } from "lucide-react";

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
}

export function DashboardLayout({ children, title, subtitle }: DashboardLayoutProps) {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar />
        <div className="flex-1 flex flex-col min-h-screen">
          <header className="h-16 flex items-center justify-between px-6 border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-10">
            <div className="flex items-center gap-4">
              <SidebarTrigger className="text-muted-foreground hover:text-foreground" />
              {title && (
                <div>
                  <h2 className="font-display text-lg font-semibold text-foreground">{title}</h2>
                  {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
                </div>
              )}
            </div>
            <div className="flex items-center gap-3">
              <button className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors">
                <Search className="h-4 w-4" />
              </button>
              <button className="h-9 w-9 rounded-lg bg-secondary flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors relative">
                <Bell className="h-4 w-4" />
                <div className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-primary" />
              </button>
              <div className="h-9 w-9 rounded-lg bg-primary/20 flex items-center justify-center text-primary font-display font-bold text-sm">
                U
              </div>
            </div>
          </header>
          <main className="flex-1 p-6 overflow-auto scrollbar-thin">
            {children}
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
