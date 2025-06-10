import { notFound } from "next/navigation";
import { allConnectorParams, connectorCategories } from "@/lib/connectors"; // Adjusted import path
import ConnectorDetailClient from "./connector-detail-client";

export function generateStaticParams() {
  // We need to generate params for each search_space_id and connector_id combination.
  // However, generateStaticParams for a dynamic segment ([connector_id])
  // only needs to return the params for that segment.
  // The `search_space_id` will be available from the parent layout or page.
  // The `allConnectorParams` already provides { connector_id: string }[]
  return allConnectorParams;
}

interface ConnectorDetailPageProps {
  params: {
    search_space_id: string;
    connector_id: string;
  };
}

export default function ConnectorDetailPage({
  params,
}: ConnectorDetailPageProps) {
  const searchSpaceId = params.search_space_id as string;
  const connectorId = params.connector_id as string;

  const connector = connectorCategories
    .flatMap((category) => category.connectors)
    .find((c) => c.id === connectorId);

  if (!connector) {
    notFound(); // Ensure connector exists before attempting to pass its ID
  }

  return (
    <ConnectorDetailClient
      connectorId={connectorId} // Pass connectorId
      searchSpaceId={searchSpaceId}
    />
  );
}