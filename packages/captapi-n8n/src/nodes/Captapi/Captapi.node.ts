import {
	NodeApiError,
	NodeOperationError,
	type IDataObject,
	type IExecuteFunctions,
	type IHttpRequestMethods,
	type INodeExecutionData,
	type INodeProperties,
	type INodeType,
	type INodeTypeDescription,
	type JsonObject,
} from 'n8n-workflow';

import { ENDPOINTS, type Endpoint, type Platform } from '../../catalog';

const VERSION = '0.1.0';

const PLATFORM_LABELS: Record<Platform, string> = {
	youtube: 'YouTube',
	tiktok: 'TikTok',
	instagram: 'Instagram',
	facebook: 'Facebook',
	twitter: 'Twitter / X',
	reddit: 'Reddit',
	threads: 'Threads',
	bluesky: 'Bluesky',
	pinterest: 'Pinterest',
	linkedin: 'LinkedIn',
	rumble: 'Rumble',
	tiktok_shop: 'TikTok Shop',
	github: 'GitHub',
	ad_library: 'Ad Library',
	google: 'Google',
	twitch: 'Twitch',
	spotify: 'Spotify',
	soundcloud: 'SoundCloud',
	linktree: 'Linktree',
	snapchat: 'Snapchat',
	truth_social: 'Truth Social',
	kick: 'Kick',
	amazon_shop: 'Amazon Shop',
	age_gender: 'Age and Gender',
	account: 'Account',
	kwai: 'Kwai',
	komi: 'Komi',
	pillar: 'Pillar',
	linkbio: 'Linkbio',
	linkme: 'Linkme',
};

const PLATFORMS = Array.from(new Set(ENDPOINTS.map((e) => e.platform))).map(
	(platform) => ({ value: platform, name: PLATFORM_LABELS[platform] ?? platform }),
);

// Friendly field labels for the known parameter names in the catalog.
const PARAM_LABELS: Record<string, string> = {
	url: 'URL',
	q: 'Query',
	query: 'Query',
	limit: 'Limit',
	language: 'Language',
	comment_id: 'Comment ID',
	country: 'Country',
};

function labelFor(name: string): string {
	if (PARAM_LABELS[name]) return PARAM_LABELS[name];
	return name
		.split('_')
		.map((w) => w.charAt(0).toUpperCase() + w.slice(1))
		.join(' ');
}

// Build the full property list (resource + per-platform operations + per-endpoint
// fields) directly from the shared catalog, so the node always matches the API.
function buildProperties(): INodeProperties[] {
	const props: INodeProperties[] = [];

	props.push({
		displayName: 'Platform',
		name: 'resource',
		type: 'options',
		noDataExpression: true,
		options: PLATFORMS.map((p) => ({ name: p.name, value: p.value })),
		default: 'youtube',
	});

	for (const p of PLATFORMS) {
		const eps = ENDPOINTS.filter((e) => e.platform === p.value);
		props.push({
			displayName: 'Operation',
			name: 'operation',
			type: 'options',
			noDataExpression: true,
			displayOptions: { show: { resource: [p.value] } },
			options: eps.map((e) => ({
				name: e.name,
				value: e.tool,
				description: e.summary,
				action: e.name,
			})),
			default: eps.length ? eps[0].tool : '',
		});
	}

	for (const e of ENDPOINTS) {
		for (const param of e.params) {
			props.push({
				displayName: labelFor(param.name),
				name: param.name,
				type: param.type === 'number' ? 'number' : param.type === 'boolean' ? 'boolean' : 'string',
				required: param.required,
				default: param.type === 'number' ? 0 : param.type === 'boolean' ? false : '',
				description: param.description,
				displayOptions: {
					show: {
						resource: [e.platform],
						operation: [e.tool],
					},
				},
			});
		}
	}

	return props;
}

export class Captapi implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'Captapi',
		name: 'captapi',
		icon: 'fa:photo-video',
		iconColor: 'purple',
		group: ['transform'],
		version: 1,
		subtitle: '={{$parameter["operation"]}}',
		description:
			'Structured social media data from 29 platforms (YouTube, TikTok, Instagram, Facebook, X, Reddit, Threads, Bluesky, Pinterest, LinkedIn, Rumble, Truth Social, Kick, Kwai, Komi, Pillar, Linkbio, Linkme, Amazon Shop) — transcripts, AI summaries, comments, stats, search and downloads.',
		defaults: {
			name: 'Captapi',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'captapiApi',
				required: true,
			},
		],
		requestDefaults: {
			baseURL: '={{$credentials.baseUrl}}',
		},
		properties: buildProperties(),
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];

		const credentials = await this.getCredentials('captapiApi');
		const baseUrl = String(credentials.baseUrl || 'https://api.captapi.com').replace(/\/+$/, '');

		const byTool = new Map<string, Endpoint>(ENDPOINTS.map((e) => [e.tool, e]));

		for (let i = 0; i < items.length; i++) {
			try {
				const operation = this.getNodeParameter('operation', i) as string;
				const endpoint = byTool.get(operation);
				if (!endpoint) {
					throw new NodeOperationError(this.getNode(), `Unknown operation: ${operation}`, {
						itemIndex: i,
					});
				}

				const qs: IDataObject = {};
				for (const param of endpoint.params) {
					const value = this.getNodeParameter(param.name, i, '') as string | number | boolean;
					const isEmpty =
						value === '' ||
						value === undefined ||
						value === null ||
						(param.type === 'number' && Number(value) === 0) ||
						(param.type === 'boolean' && value === false);
					if (!isEmpty) qs[param.name] = value;
				}

				const responseData = await this.helpers.httpRequestWithAuthentication.call(
					this,
					'captapiApi',
					{
						method: 'GET' as IHttpRequestMethods,
						baseURL: baseUrl,
						url: endpoint.path,
						qs,
						json: true,
						headers: {
							'User-Agent': `n8n-nodes-captapi/${VERSION}`,
						},
					},
				);

				returnData.push({
					json: (responseData ?? {}) as IDataObject,
					pairedItem: { item: i },
				});
			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({
						json: { error: (error as Error).message },
						pairedItem: { item: i },
					});
					continue;
				}
				if (error instanceof NodeOperationError) throw error;
				throw new NodeApiError(this.getNode(), error as JsonObject, { itemIndex: i });
			}
		}

		return [returnData];
	}
}
