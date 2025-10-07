"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Sparkles, Menu, Bell, Github } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { UserMenu } from "@/components/UserMenu";

interface TopbarProps {
  onMenuClick: () => void;
}

export function Topbar({ onMenuClick }: TopbarProps) {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white/80 backdrop-blur-sm border-b border-stone-200 z-40">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Left Section */}
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={onMenuClick}
            className="lg:hidden hover:bg-stone-100"
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex items-center gap-2">
            <div className="h-8 w-8 bg-stone-900 rounded-lg flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <div className="hidden sm:flex items-center gap-2">
              <h1 className="text-xl font-bold text-stone-900">GitRot</h1>
              <Badge
                variant="secondary"
                className="bg-stone-200 text-stone-700 text-xs"
              >
                AI-Powered
              </Badge>
            </div>
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-2">
          {/* GitHub Link */}
          <Button
            variant="ghost"
            size="sm"
            asChild
            className="hidden md:flex hover:bg-stone-100"
          >
            <a
              href="https://github.com/mcaupybugs/GitRot"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="h-5 w-5 mr-2" />
              <span className="text-sm">Star on GitHub</span>
            </a>
          </Button>

          {/* Notifications */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="relative hover:bg-stone-100"
              >
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 h-4 w-4 bg-red-500 rounded-full text-[10px] text-white flex items-center justify-center font-medium">
                  2
                </span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80">
              <DropdownMenuLabel>Notifications</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <div className="p-2 space-y-2">
                <div className="p-2 rounded-lg hover:bg-stone-50 cursor-pointer">
                  <p className="text-sm font-medium">New feature available!</p>
                  <p className="text-xs text-stone-500 mt-1">
                    Try our enhanced README generation with better formatting.
                  </p>
                  <p className="text-xs text-stone-400 mt-1">2 hours ago</p>
                </div>
                <div className="p-2 rounded-lg hover:bg-stone-50 cursor-pointer">
                  <p className="text-sm font-medium">Generation complete</p>
                  <p className="text-xs text-stone-500 mt-1">
                    Your README for repository &quot;awesome-project&quot; is
                    ready.
                  </p>
                  <p className="text-xs text-stone-400 mt-1">5 hours ago</p>
                </div>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* User Menu */}
          <UserMenu />
        </div>
      </div>
    </header>
  );
}
