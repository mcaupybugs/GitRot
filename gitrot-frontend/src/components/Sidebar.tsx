"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Settings,
  FileText,
  History,
  HelpCircle,
  Home,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navigationItems = [
  {
    title: "Home",
    icon: Home,
    href: "/",
    badge: null,
  },
  {
    title: "Generate README",
    icon: FileText,
    href: "/",
    badge: null,
  },
  {
    title: "History",
    icon: History,
    href: "/history",
    badge: "Soon",
  },
  {
    title: "Settings",
    icon: Settings,
    href: "/settings",
    badge: null,
  },
  {
    title: "Help",
    icon: HelpCircle,
    href: "/help",
    badge: null,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [isHovered, setIsHovered] = React.useState(false);

  // Sidebar expands only on hover
  const isExpanded = isHovered;

  return (
    <aside
      className={cn(
        "fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white border-r border-stone-200 transition-all duration-300 ease-in-out z-30",
        isExpanded ? "w-64" : "w-16"
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="flex flex-col h-full">
        {/* Navigation Items */}
        <nav className="flex-1 p-3 space-y-1 pt-4">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href;

            return (
              <Link key={item.title} href={item.href}>
                <Button
                  variant="ghost"
                  className={cn(
                    "w-full justify-start transition-colors relative group",
                    isActive
                      ? "bg-stone-100 text-stone-900 hover:bg-stone-150"
                      : "text-stone-600 hover:bg-stone-50 hover:text-stone-900",
                    isExpanded ? "px-3" : "px-2 justify-center"
                  )}
                  title={!isExpanded ? item.title : undefined}
                >
                  <Icon
                    className={cn(
                      "h-5 w-5 flex-shrink-0",
                      isExpanded && "mr-3"
                    )}
                  />
                  {isExpanded && (
                    <>
                      <span className="flex-1 text-left">{item.title}</span>
                      {item.badge && (
                        <Badge
                          variant="secondary"
                          className="bg-amber-100 text-amber-700 text-xs"
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </>
                  )}
                </Button>
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Footer */}
        <div className="border-t border-stone-200">
          {isExpanded && (
            <div className="p-4">
              <div className="bg-stone-50 rounded-lg p-3 border border-stone-200">
                <div className="flex items-center gap-2 mb-2">
                  <User className="h-4 w-4 text-stone-600" />
                  <p className="text-xs font-medium text-stone-700">Account</p>
                </div>
                <p className="text-xs text-stone-500">
                  Manage your profile and preferences
                </p>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full mt-3 text-xs border-stone-200 hover:bg-stone-100"
                >
                  View Profile
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
