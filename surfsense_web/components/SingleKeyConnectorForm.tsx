"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input }  from "@/components/ui/input";
import { useToast } from "@/components/ui/use-toast"; // Corrected import for useToast

interface Props {
  /** Backend connector_type constant, e.g. "TODOIST_CONNECTOR" */
  connectorType: string;
  /** Human label to display, e.g. "Todoist API Key" */
  label: string;
  /** Current search space id for redirect/association */
  searchSpaceId: string;
  /** Optional onSuccess callback (e.g. refetch list) */
  onSuccess?: () => void;
}

export default function SingleKeyConnectorForm({
  connectorType,
  label,
  searchSpaceId,
  onSuccess,
}: Props) {
  const [secret, setSecret] = useState("");
  const [loading, setLoading] = useState(false);
  const { toast } = useToast(); // Correct usage of useToast

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!secret) return;

    setLoading(true);
    try {
      const res = await fetch("/api/v1/search-source-connectors/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: `${connectorType.replace("_CONNECTOR", "").replace("_", " ")} Connector`, // Generates a name like "TODOIST Connector"
          connector_type: connectorType,
          search_space_id: Number(searchSpaceId),
          config: { [`${connectorType.replace("_CONNECTOR", "")}_API_KEY`]: secret },
        }),
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ message: res.statusText }));
        throw new Error(errorData.message || `Request failed with status ${res.status}`);
      }
      toast({ title: "Success!", description: `${label.replace(" API Key", "")} connector added successfully.` });
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: any) {
      toast({ variant: "destructive", title: "Error adding connector", description: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-sm">
      <div className="space-y-1">
        <label htmlFor={connectorType + "-secret"} className="block text-sm font-medium text-muted-foreground">{label}</label>
        <Input
          id={connectorType + "-secret"}
          type="password"
          value={secret}
          onChange={e => setSecret(e.target.value)}
          placeholder="Enter your API key"
          required
          className="mt-1"
        />
      </div>
      <Button disabled={loading || !secret} type="submit" className="w-full">
        {loading ? "Connecting…" : "Connect"}
      </Button>
    </form>
  );
}