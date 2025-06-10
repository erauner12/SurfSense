"use client";

import { Connector, connectorCategories } from "@/lib/connectors";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { IconArrowLeft } from "@tabler/icons-react";
import SingleKeyConnectorForm from "@/components/SingleKeyConnectorForm"; // Import the new form

interface ConnectorDetailClientProps {
  connectorId: string;
  searchSpaceId: string;
}

export default function ConnectorDetailClient({ connectorId, searchSpaceId }: ConnectorDetailClientProps) {
  const connector = connectorCategories
    .flatMap((c) => c.connectors)
    .find((c) => c.id === connectorId);

  if (!connector) {
    return (
        <div className="container mx-auto py-12 max-w-3xl text-center">
            <p className="text-red-500">Connector data could not be loaded.</p>
            <Link href={`/dashboard/${searchSpaceId}/connectors/add`}>
              <Button variant="outline" size="sm" className="mt-4">
                <IconArrowLeft className="mr-2 h-4 w-4" />
                Back to Connectors
              </Button>
            </Link>
        </div>
    );
  }

  return (
    <div className="container mx-auto py-12 max-w-3xl">
      <div className="mb-8">
        <Link href={`/dashboard/${searchSpaceId}/connectors/add`}>
          <Button variant="outline" size="sm">
            <IconArrowLeft className="mr-2 h-4 w-4" />
            Back to Connectors
          </Button>
        </Link>
      </div>

      <div className="bg-card p-8 rounded-lg shadow-lg">
        <div className="flex items-center mb-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-primary/10 dark:bg-primary/20 mr-6">
            <div className="text-primary text-3xl">
              {connector.icon}
            </div>
          </div>
          <div>
            <h1 className="text-3xl font-bold">{connector.title}</h1>
            <p className="text-muted-foreground">{connector.description}</p>
          </div>
        </div>
        
        <div className="space-y-4">
          <p>
            <strong>Status:</strong>
            {connector.status === "available" && <span className="text-green-600 ml-1">Available</span>}
            {connector.status === "coming-soon" && <span className="text-amber-600 ml-1">Coming Soon</span>}
            {connector.status === "connected" && <span className="text-blue-600 ml-1">Connected</span>}
          </p>
          
          <p><strong>Search Space ID:</strong> {searchSpaceId}</p>
          <p><strong>Connector ID:</strong> {connectorId}</p>

          <div className="mt-8 pt-6 border-t">
            <h2 className="text-xl font-semibold mb-4">Configuration</h2>
            {connector.status === "available" && (
              connector.id === "todoist-connector" ? (
                <SingleKeyConnectorForm
                  connectorType="TODOIST_CONNECTOR"
                  label="Todoist API Key"
                  searchSpaceId={searchSpaceId}
                  onSuccess={() => {
                    // Navigate to the connectors list page after successful connection
                    window.location.href = `/dashboard/${searchSpaceId}/connectors`;
                  }}
                />
              ) : (
                <p className="text-muted-foreground">
                  Connection form for "{connector.title}" will be displayed here.
                </p>
              )
            )}
            {connector.status === "coming-soon" && (
              <p className="text-muted-foreground">
                This connector is coming soon. Configuration will be available once released.
              </p>
            )}
            {connector.status === "connected" && (
              <p className="text-muted-foreground">
                Manage your existing "{connector.title}" connection.
              </p>
            )}
            
            <div className="mt-6">
              {/* Show generic connect button only if status is available AND it's NOT Todoist */}
              {connector.status === "available" && connector.id !== "todoist-connector" && (
                <Button>Connect {connector.title}</Button>
              )}
              {connector.status === "connected" && (
                <Button variant="destructive">Disconnect</Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}