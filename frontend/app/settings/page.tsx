"use client";

import React from "react";
import { redirect } from "next/navigation";

export default function SettingsPage() {
  redirect("/settings/appearance");
}
