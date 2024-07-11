document.addEventListener("DOMContentLoaded", () => {
    let currentTeamIndex = 0;
    let settings = {};
    const draftedPlayers = {};
    let done = false;

    const teamList = document.getElementById("team-list");
    const availablePlayersLists = {
        overall: document.getElementById("available-players-overall"),
        QB: document.getElementById("available-players-QB"),
        RB: document.getElementById("available-players-RB"),
        WR: document.getElementById("available-players-WR"),
        TE: document.getElementById("available-players-TE"),
        K: document.getElementById("available-players-K"),
        DST: document.getElementById("available-players-DST"),
    };
    const draftedPlayersList = document.getElementById("drafted-players");
    const sleeperDraftIdInput = document.getElementById("sleeper-draft-id");
    const connectBtn = document.getElementById("connect-btn");
    const optimizeBtn = document.getElementById("optimize-btn");
    const teamSelect = document.getElementById("team-select");
    const flashMessage = document.getElementById("flash-message-Sleeper");
    const tabLinks = document.querySelectorAll(".tab-link");

    connectBtn.addEventListener("click", connectToSleeperDraft);
    optimizeBtn.addEventListener("click", optimize);
    teamSelect.addEventListener("change", teamSelectChange);

    tabLinks.forEach(tab => {
        tab.addEventListener("click", () => {
            tabLinks.forEach(link => link.classList.remove("active"));
            tab.classList.add("active");
            const tabContent = tab.dataset.tab;
            document.querySelectorAll(".tab-content").forEach(content => {
                content.classList.remove("active");
            });
            availablePlayersLists[tabContent].classList.add("active");
            highlightPlayerIfSelected(tabContent);
        });
    });

    async function connectToSleeperDraft() {
        const recommendedPlayer = document.querySelector(`#Recommendation`);
        recommendedPlayer.textContent = ``;
        const draftId = sleeperDraftIdInput.value;
        if (draftId) {
            done = false;
            const draftData = await fetchSleeperDraftData(draftId);
            initialize(draftData);
            showFlashMessage("Successfully connected!");
        }
    }

    async function fetchSleeperDraftData(draftId) {
        try {
            const picksResponse = await fetch(`https://api.sleeper.app/v1/draft/${draftId}/picks`);
            const picksData = await picksResponse.json();
            const draftResponse = await fetch(`https://api.sleeper.app/v1/draft/${draftId}`);
            const draftData = await draftResponse.json();
            const keys = Object.keys(draftData.settings);
            const QBs = draftData.settings[keys[4]];
            const RBs = draftData.settings[keys[3]];
            const WRs = draftData.settings[keys[1]];
            const TEs = draftData.settings[keys[2]];
            const Ks = draftData.settings[keys[5]];
            const DSTs = draftData.settings[keys[7]];
            const flex = draftData.settings[keys[6]];
            const bn = draftData.settings[keys[8]]-QBs-RBs-WRs-TEs-Ks-DSTs-flex;
            const teams = draftData.settings[keys[0]];
            //const scoring = data.metadata[keys[0]];
            settings = {
                QBs: QBs,
                RBs: RBs,
                WRs: WRs,
                TEs: TEs,
                Ks: Ks,
                DSTs: DSTs,
                flex: flex,
                Bench: bn,
                teams: teams,
                //scoring: scoring
            }
            return { settings, picksData };
        } catch (error) {
            console.error('Error fetching Sleeper draft data:', error);
            return null;
        }
    }

    async function initialize({ settings, picksData }) {
        if (settings) {
            const numOfTeams = settings.teams;
            const teams = Array.from({ length: numOfTeams }, (_, index) => `Team ${index + 1}`);
  
            teamList.innerHTML = '';
            
            if (teamSelect.length == 0) {
                teamSelect.innerHTML = '';
            }

            teams.forEach((team, index) => {
                const teamItem = document.createElement("li");
                teamItem.textContent = team;
                if (index === currentTeamIndex) {
                    teamItem.classList.add("active");
                }
                teamList.appendChild(teamItem);

                const option = document.createElement("option");
                option.value = team;
                option.textContent = team;
                if (teamSelect.length < teams.length) {
                    teamSelect.appendChild(option);
                }
            });
            if (picksData.length >= settings.teams * (settings.QBs + settings.RBs + settings.WRs + settings.TEs + settings.Ks + settings.DSTs + settings.flex + settings.Bench)) {
                done = true;
            }
            adjustCurrentPick(picksData.length, teams);
            updateDraftedPlayersList(picksData, teams);
            displayRosterRequirements(settings);
            const availablePlayers = await fetchAvailablePlayers();
            populatePlayers(availablePlayers);
        } else {
            console.error('Error: Could not find number of teams in API response');
        }
    }

    function highlightPlayerIfSelected(position) {
        const activePlayer = document.querySelector('#players-list li.active');
        if (activePlayer && activePlayer.textContent.includes(position)) {
            const playerName = activePlayer.textContent.split(' (')[0];
            highlightPlayer(playerName);
        }
    }

    async function fetchAvailablePlayers() {
        try {
            const playersData = await readCSVFiles();
            playersData.sort((a, b) => b.FPTS - a.FPTS);

            const availablePlayers = playersData.filter(player => {
                for (const teamPlayers of Object.values(draftedPlayers)) {
                    if (teamPlayers.some(draftedPlayer => draftedPlayer.Player.replace(/\./g, '') === player.Player)) {
                        return false;
                    }
                }
                return true;
            });

            return availablePlayers;
        } catch (error) {
            console.error('Error fetching available players:', error);
            return [];
        }
    }

    function populatePlayers(players) {
        Object.values(availablePlayersLists).forEach(list => list.innerHTML = '');

        players.forEach(player => {
            const playerItem = document.createElement("li");
            const teamText = player.Pos === 'DST' ? '' : ` - ${player.Team}`;
            playerItem.textContent = `${player.Player} (${player.Pos})${teamText}`;
            const vorp = document.createElement("span");
            vorp.classList = "vorp";
            vorp.textContent = `VORP: ${player.FPTS}`
            playerItem.appendChild(vorp);
            availablePlayersLists.overall.appendChild(playerItem);
            availablePlayersLists[player.Pos].appendChild(playerItem.cloneNode(true));
        });
    }

    function updateDraftedPlayersList(data, teams) {
        draftedPlayersList.innerHTML = "";
        let pickNumber = 1;
        let isAscending = true;

        data.forEach(pick => {
            const teamName = `Team ${calculateTeamIndex(pickNumber, teams.length) + 1}`;
            if (!draftedPlayers[teamName]) {
                draftedPlayers[teamName] = [];
            }
            if (pick.pick_no <= teams.length) {
                draftedPlayers[teamName] = [];
            }

            draftedPlayers[teamName].push({
                Player: `${pick.metadata.first_name} ${pick.metadata.last_name}`,
                Team: pick.metadata.team,
                Pos: pick.metadata.position
            });

            pickNumber += isAscending ? 1 : -1;
            if (pickNumber < 1 || pickNumber > teams.length) {
                isAscending = !isAscending;
                pickNumber = isAscending ? 1 : teams.length;
            }
        });
    }

    function adjustCurrentPick(draftedCount, teams) {
        const round = Math.floor(draftedCount / teams.length);
        currentTeamIndex = draftedCount % teams.length;
        const isAscending = (round % 2 === 0);
        currentTeamIndex = isAscending ? currentTeamIndex : teams.length - currentTeamIndex - 1;
        highlightCurrentTeam();
    }

    function highlightCurrentTeam() {
        const teamItems = document.querySelectorAll("#team-list li");
        teamItems.forEach(item => item.classList.remove("active"));
        teamItems[currentTeamIndex].classList.add("active");
    }

    function calculateTeamIndex(pickNumber, numberOfTeams) {
        const roundNumber = Math.ceil(pickNumber / numberOfTeams);
        const withinRoundNumber = pickNumber % numberOfTeams;
        const isEvenRound = roundNumber % 2 === 0;
        return isEvenRound ? numberOfTeams - withinRoundNumber - 1 : withinRoundNumber - 1;
    }

    async function optimize() {
        if (done) {
            showFlashMessage("Draft is complete!", 'done');
            return;
        }
        try {
            showFlashMessage("Optimizing...", 'optimizing');
            const response = await fetch('http://127.0.0.1:5000/process-info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    draft_id: sleeperDraftIdInput.value,
                    personal_team: currentTeamIndex+1
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();
            highlightPlayer(result);
            const recommendedPlayer = document.querySelector(`#Recommendation`);
            recommendedPlayer.textContent = `Recommended Player: ${result}`;

            showFlashMessage("Done!", 'done');
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function highlightPlayer(player) {
        const playerItems = document.querySelectorAll("#players-list li");
        playerItems.forEach(item => item.classList.remove("active"));
        playerItems.forEach(item => {
            if (item.textContent.includes(player)) {
                item.classList.add("active");
            }
        });
    }

    async function displayRosterRequirements(settings) {
        const rosterRequirements = document.createElement("div");
        rosterRequirements.classList.add("roster-requirements");

        // Helper function to create list items for each position
        function createPositionListItems(position, count, players = [], flexPlayers = [], benchPlayers = []) {
            let listItems = '';
            let playerIndex = 0;
            for (let i = 0; i < count; i++) {
                const player = players[playerIndex];
                if (player) {
                    listItems += `<li>${position}: ${player.Player}</li>`;
                    playerIndex++;
                } else {
                    listItems += `<li>${position}</li>`;
                }
            }
    
            // Add remaining players to flex positions
            while (playerIndex < players.length && flexPlayers.length < settings.flex && (position === 'WR' || position === 'RB' || position === 'TE')) {
                flexPlayers.push(players[playerIndex]);
                playerIndex++;
            }
    
            // Add remaining players to bench positions
            while (playerIndex < players.length && benchPlayers.length < settings.Bench) {
                benchPlayers.push(players[playerIndex]);
                playerIndex++;
            }
    
            return listItems;
        }
    
        // Get drafted players (assuming a global object draftedPlayers or a function to fetch them)
        // Example: const draftedPlayers = await getDraftedPlayers(draft_id);
    
        const selectedTeam = teamSelect.value; // Assume this is the team for which you want to display roster
        const teamDraftedPlayers = draftedPlayers[selectedTeam] || [];
    
        const positions = {
            'QB': settings.QBs,
            'RB': settings.RBs,
            'WR': settings.WRs,
            'TE': settings.TEs,
            'K': settings.Ks,
            'DST': settings.DSTs,
            'Flex': settings.flex,
            'Bench': settings.Bench
        };

        let flexPlayers = [];
        let benchPlayers = [];
        for (let i = 0; i < teamDraftedPlayers.length; i++) {
            if (teamDraftedPlayers[i].Pos === 'DEF') {
                teamDraftedPlayers[i].Pos = 'DST';
            }
        }
        rosterRequirements.innerHTML = `
            <h3></h3>
            <ul>
                ${createPositionListItems('QB', positions.QB, teamDraftedPlayers.filter(p => p.Pos === 'QB'), [], benchPlayers)}
                ${createPositionListItems('RB', positions.RB, teamDraftedPlayers.filter(p => p.Pos === 'RB'), flexPlayers, benchPlayers)}
                ${createPositionListItems('WR', positions.WR, teamDraftedPlayers.filter(p => p.Pos === 'WR'), flexPlayers, benchPlayers)}
                ${createPositionListItems('TE', positions.TE, teamDraftedPlayers.filter(p => p.Pos === 'TE'), flexPlayers, benchPlayers)}
                ${createPositionListItems('Flex', positions.Flex, flexPlayers, [], benchPlayers)}
                ${createPositionListItems('K', positions.K, teamDraftedPlayers.filter(p => p.Pos === 'K'), [], benchPlayers)}
                ${createPositionListItems('DST', positions.DST, teamDraftedPlayers.filter(p => p.Pos === 'DST'), [], benchPlayers)}
                ${createPositionListItems('Bench', positions.Bench, benchPlayers)}
            </ul>
        `;
        document.getElementById("drafted-players").appendChild(rosterRequirements);
    }

    function showFlashMessage(message, type = 'connected') {
        flashMessage.textContent = message;
        flashMessage.style.display = 'inline-block';
        if (type === 'connected') {
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 1000);
        }
        else if (type === 'optimizing') {
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 10000);
        }
        else {
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 1000);
        }
    }

    function teamSelectChange(){
        draftedPlayersList.innerHTML = "";
        displayRosterRequirements(settings);
    }

    async function readCSVFiles() {
        // Array to store all player data from CSV files
        const allPlayersData = [];
    
        // Names of CSV files
        // const csvFiles = ['FantasyPros_Fantasy_Football_Projections_K.csv', 'FantasyPros_Fantasy_Football_Projections_DST.csv', 'FantasyPros_Fantasy_Football_Projections_WR.csv', 'FantasyPros_Fantasy_Football_Projections_QB.csv', 'FantasyPros_Fantasy_Football_Projections_RB.csv', 'FantasyPros_Fantasy_Football_Projections_TE.csv'];
        const csvFile = ['vorp2024.csv']
        // Read each CSV file and extract 'Player', 'Team', and 'FPTS' columns
        const response = await fetch(csvFile);
        const text = await response.text();
        const csvData = Papa.parse(text, { header: true }).data;

        const filteredData = csvData.filter(player => player.Player.trim() !== '');

        // Extract and retain only the required columns
        const extractedData = filteredData.map(player => ({
            Player: player.Player.replace(/\./g, ''),
            Team: player.Team,
            FPTS: player.VORP,
            Pos: player.POS
        }));

        allPlayersData.push(...extractedData);
        

        return allPlayersData;
    }
});
