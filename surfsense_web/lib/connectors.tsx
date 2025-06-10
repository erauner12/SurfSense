import React from 'react';
import {
  IconBrandDiscord,
  IconBrandGithub,
  IconBrandNotion,
  IconBrandSlack,
  IconChecklist,
  IconBrandWindows,
  IconBrandZoom,
  IconMail,
  IconWorldWww,
  IconTicket,
  IconLayoutKanban,
  IconLinkPlus,
} from "@tabler/icons-react";

// Define the Connector type
export interface Connector {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  status: "available" | "coming-soon" | "connected";
}

export interface ConnectorCategory {
  id: string;
  title: string;
  connectors: Connector[];
}

// Define connector categories and their connectors
export const connectorCategories: ConnectorCategory[] = [
  {
    id: "search-engines",
    title: "Search Engines",
    connectors: [
      {
        id: "tavily-api",
        title: "Tavily API",
        description: "Search the web using the Tavily API",
        icon: <IconWorldWww className="h-6 w-6" />,
        status: "available",
      },
      {
        id: "linkup-api",
        title: "Linkup API",
        description: "Search the web using the Linkup API",
        icon: <IconLinkPlus className="h-6 w-6" />,
        status: "available",
      },
    ],
  },
  {
    id: "team-chats",
    title: "Team Chats",
    connectors: [
      {
        id: "slack-connector",
        title: "Slack",
        description: "Connect to your Slack workspace to access messages and channels.",
        icon: <IconBrandSlack className="h-6 w-6" />,
        status: "available",
      },
      {
        id: "ms-teams",
        title: "Microsoft Teams",
        description: "Connect to Microsoft Teams to access your team's conversations.",
        icon: <IconBrandWindows className="h-6 w-6" />,
        status: "coming-soon",
      },
      {
        id: "discord-connector",
        title: "Discord",
        description: "Connect to Discord servers to access messages and channels.",
        icon: <IconBrandDiscord className="h-6 w-6" />,
        status: "available"
      },
    ],
  },
  {
    id: "project-management",
    title: "Project Management",
    connectors: [
      {
        id: "linear-connector",
        title: "Linear",
        description: "Connect to Linear to search issues, comments and project data.",
        icon: <IconLayoutKanban className="h-6 w-6" />,
        status: "available",
      },
      {
        id: "jira-connector",
        title: "Jira",
        description: "Connect to Jira to search issues, tickets and project data.",
        icon: <IconTicket className="h-6 w-6" />,
        status: "coming-soon",
      },
      {
        id: "todoist-connector",
        title: "Todoist",
        description: "Connect to Todoist to access tasks, priorities and deadlines.",
        icon: <IconChecklist className="h-6 w-6" />,
        status: "available",
      },
    ],
  },
  {
    id: "knowledge-bases",
    title: "Knowledge Bases",
    connectors: [
      {
        id: "notion-connector",
        title: "Notion",
        description: "Connect to your Notion workspace to access pages and databases.",
        icon: <IconBrandNotion className="h-6 w-6" />,
        status: "available",
      },
      {
        id: "github-connector",
        title: "GitHub",
        description: "Connect a GitHub PAT to index code and docs from accessible repositories.",
        icon: <IconBrandGithub className="h-6 w-6" />,
        status: "available",
      },
    ],
  },
  {
    id: "communication",
    title: "Communication",
    connectors: [
      {
        id: "gmail",
        title: "Gmail",
        description: "Connect to your Gmail account to access emails.",
        icon: <IconMail className="h-6 w-6" />,
        status: "coming-soon",
      },
      {
        id: "zoom",
        title: "Zoom",
        description: "Connect to Zoom to access meeting recordings and transcripts.",
        icon: <IconBrandZoom className="h-6 w-6" />,
        status: "coming-soon",
      },
    ],
  },
];

// Provides the structure { connector_id: string }[] expected by generateStaticParams
export const allConnectorParams = connectorCategories
  .flatMap(category => category.connectors)
  .map(connector => ({ connector_id: connector.id }));