<script>
	import Award from '$lib/components/award.svelte';
	export const pubs = [
		{
			title:
				'A Neuro-Symbolic Architecture for Efficient Classification using Hyperdimensional Computing',
			auth: 'Rishikanth Chandrasekaran, Tajana Rosing',
			venue: 'ISLPED',
			date: 2024
		},
		{
			title: 'Federated Hyperdimensional Computing',
			auth: 'Kazim Ergun, Rishikanth Chandrasekaran, Tajana Rosing',
			venue: 'ACM TIoT (under review)',
			date: 2023
		},
		{
			title: 'Multi-label classification with Hyperdimensional Representations',
			auth: 'Rishikanth Chandrasekaran, F Asgareinjad, J Morris, T Rosing',
			venue: 'IEEE Access Journal',
			date: 2023
		},
		{
			title: 'Fhdnn: Communication efficient and robust federated learning for aiot networks',
			auth: 'R Chandrasekaran, K Ergun, J Lee, D Nanjunda, J Kang, T Rosing',
			venue: 'Proceedings of the 59th ACM/IEEE Design Automation Conference',
			date: 2022
		},
		{
			title:
				'Hdnn-pim: Efficient in memory design of hyperdimensional computing with feature extraction',
			auth: 'A Dutta, S Gupta, B Khaleghi, R Chandrasekaran, W Xu, T Rosing',
			venue: 'Proceedings of the Great Lakes Symposium on VLSI',
			date: 2022
		},
		{
			title: 'A drone-based system for intelligent and autonomous homes',
			auth: 'S Xia, R Chandrasekaran, Y Liu, C Yang, TS Rosing, X Jiang',
			venue: 'Proceedings of the 19th ACM Conference on Embedded Networked Sensor Systems',
			date: 2021,
			award: 'Best Demo'
		},
		{
			title: 'Efficient Sparse Processing for Smart Home Applications',
			auth: 'Rishikanth Chandrasekaran, Yunhui Guo, Anthony Thomas, Masimiliano Menarini, Michael Ostertag, Tajana Rosing',
			venue: 'ACM Conference on Embedded Network Sensor Systems (SenSys)',
			date: 2019
		},
		{
			title:
				'A Scalable System for Apportionment and Tracking of Energy Footprints in Commercial Buildings',
			auth: 'Peter Wei, Xiaoqi Chen, Jordan Vega, Stephen Xia, Rishikanth Chandrasekaran, Xiaofan Jiang',
			venue: 'ACM Transaction on Sensor Networks (TSON)',
			date: 2018
		},
		{
			title: 'PAWS: A Wearable Acoustic System for Pedestrian Safety',
			auth: 'Daniel de Godoy, Bashima Islam, Stephen Xia, Md Tamzeed Islam, Rishikanth Chandrasekaran, Yen-Chun Chen, Shahriar Nirjon, Peter R Kinget, Xiaofan Jiang',
			venue: 'Internet-of-Things Design and Implementation (IoTDI)',
			date: 2018
		},
		{
			title: 'Paws: A wearable acoustic system for pedestrian safety.',
			venue:
				'IEEE/ACM Third International Conference on Internet-of-Things Design and Implementation (IoTDI)',
			date: 2018,
			auth: 'Daniel de Godoy, Bashima Islam, Stephen Xia, Md Tamzeed Islam, Rishikanth Chandrasekaran, Yen-Chun Chen, Shahriar Nirjon, Peter R Kinget, Xiaofan Jiang'
		},
		{
			title:
				'ePrints a real-time and scalable system for fair apportionment and tracking of personal energy footprints in commercial buildings',
			venue:
				'ACM International Conference on Systems for Energy-Efficient Built Environments (BuildSys)',
			auth: 'P Wei, X Chen, J Vega, S Xia, R Chandrasekaran, X Jiang',
			date: 2017,
			award: 'Best Paper Runner Up'
		},
		{
			title: 'Adaptive and Personalized Energy Saving Suggestions for Occupants in Smart Buildings',
			venue:
				'ACM International Conference on Systems for Energy-Efficient Built Environments (BuildSys)',
			auth: 'P Wei, X Chen, R Chandrasekaran, F Song, X Jiang',
			date: 2016,
			award: 'Best Poster'
		},
		{
			title:
				'SEUS: A Wearable Multi-Channel Acoustic Headset Platform to Improve Pedestrian Safety',
			venue: 'ACM Conference on Embedded Network Sensor Systems (SenSys)',
			auth: 'R Chandrasekaran, D de Godoy, S Xia, MT Islam, B Islam, S Nirjon, P Kinget, X Jiang',
			date: 2016
		},
		{
			title: 'Personal energy footprint in shared building environment',
			venue: 'International Conference on Information Processing in Sensor Networks (IPSN)',
			auth: 'P Wei, X Chen, R Chandrasekaran, F Song, X Jiang',
			date: 2016
		},
		{
			title:
				'Low-cost intelligent gesture recognition engine for audio-vocally impaired individuals',
			venue: 'Global Humanitarian Technology Conference (GHTC)',
			auth: 'C Rishikanth, H Sekar, G Rajagopal, R Rajesh, V Vijayaraghavan',
			date: 2014
		}
	];
</script>

<div class="flex w-[756px] flex-col justify-start gap-8">
	{#each pubs as pub (pub.title)}
		<div class="flex flex-col">
			<div class="flex gap-2 text-lg text-gray-50">
				{pub.title}

				{#if pub.award}
					<div class="flex flex-shrink-0 items-center gap-1">
						<Award size="20" starColor="#0f62fe" />
						<div class="text-sm">{pub.award}</div>
					</div>
				{/if}
			</div>
			<div class="text-sm">{pub.auth}</div>
			<div class="text-xs italic text-blue-500">{pub.venue}</div>
		</div>
	{/each}
</div>
