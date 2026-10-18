-- ShadowCore Pet Talents: a arvore de talentos do pet do Hunter dentro da janela N (CoATalentFrame).
-- Integrada ao jogo: carregada pelo proprio Ascension_CoATalents (patch-ZZP.MPQ), nao e mais addon.
-- Nao e um sistema novo: le e grava pela API de talento de pet do 3.3.5 (GetTalentInfo/AddPreviewTalentPoints/
-- LearnPreviewTalents com isPet=true); quem valida e o servidor (CMSG_LEARN_PREVIEW_TALENTS_PET -> Player::LearnPetTalent).
-- O desenho usa o motor das arvores CoA (TalentTreeBase + nos, linhas e portoes CoA).

local PET_TAB = 1
local PER_TIER = 3          -- PET_TALENTS_PER_TIER: pontos na arvore para liberar cada tier
local ID_BASE = 990000      -- ids so da interface; nunca chegam ao C_CharacterAdvancement
local CLASS_KEY = "ShadowCorePet"
local rebuildCount = 0

local function Log(msg)
    ShadowCorePetTalentsLog = ShadowCorePetTalentsLog or {}
    local log = ShadowCorePetTalentsLog
    log[#log + 1] = date("%H:%M:%S") .. " " .. tostring(msg)
    while #log > 300 do table.remove(log, 1) end
end

local function Report(err)
    Log("ERRO " .. tostring(err))
    if DEFAULT_CHAT_FRAME then
        DEFAULT_CHAT_FRAME:AddMessage("|cffff5050ShadowCore Pet Talents:|r " .. tostring(err))
    end
end

local lastSync = 0
local function RequestSync()   -- o cliente perde os talentos do pet quando ele e chamado de novo: pede ao servidor de novo
    local now = GetTime()
    if now - lastSync < 1 then return end
    lastSync = now
    SendChatMessage(".petreset sync", "SAY")
end

local function TalentGroup()
    return GetActiveTalentGroup(false, true) or 1
end

local function IsHunter()
    return select(2, UnitClass("player")) == "HUNTER"
end

local function HasPetTree()
    return IsHunter() and HasPetUI() and PetCanBeAbandoned() and (GetNumTalents(PET_TAB, false, true) or 0) > 0
end

local function TabInfo()
    local name, icon, spent, background, previewSpent = GetTalentTabInfo(PET_TAB, false, true, TalentGroup())
    return name, icon, spent or 0, previewSpent or 0
end

local function PointsAvailable()
    local group = TalentGroup()
    local unspent = GetUnspentTalentPoints(false, true, group) or 0
    local preview = GetGroupPreviewTalentPointsSpent(true, group) or 0
    return unspent - preview, preview
end

local function TreeInvestment()
    local _, _, spent, previewSpent = TabInfo()
    return spent + previewSpent
end

-------------------------------------------------------------------------------
-- No do pet
-------------------------------------------------------------------------------
local PetNode = {}

function PetNode:SetEntry(entry)
    self.entry = entry
end

function PetNode:Query()
    local e = self.entry
    local name, icon, tier, column, rank, maxRank, isExceptional, meetsPrereq, previewRank, meetsPreviewPrereq =
        GetTalentInfo(PET_TAB, e.talentIndex, false, true, TalentGroup())
    self.talentName = name
    self.iconTexture = icon
    self.learnedRank = rank or 0
    self.rank = math.max(rank or 0, previewRank or 0)
    self.maxRank = maxRank or 1
    self.isGated = TreeInvestment() < e.RequiredInvestment
    local available = PointsAvailable()
    self.canLearn = (not self.isGated) and (meetsPreviewPrereq and true or false) and self.rank < self.maxRank and available > 0
end

function PetNode:UpdateIcon()
    if self.Icon.iconMask ~= self.artSet.iconMask then
        self.Icon:SetIconMask(self.artSet.iconMask, TextureUtil.MaskSize.Small)
    end
    if self.iconTexture then
        self.Icon:SetIcon(self.iconTexture)
    end
    self.Icon:SetBackgroundAtlas(self.artSet.shadow)
end

function PetNode:UpdateDisplay()
    if not self.entry then
        return
    end
    self:Query()
    self:UpdateIcon()
    self:UpdateRank()
    self.visualState = self:CalculateVisualState()
    self:UpdateConnectionVisual(self.visualState)
    self:ApplyVisualState(self.visualState)
    if GameTooltip:IsOwned(self) then
        self:OnEnter()
    end
end

-- seta: o filho guarda o pai em ConnectedNodes (como no DBC); acende quando o pai esta completo (regra do pet no 3.3.5)
function PetNode:CanConnect(otherEntryID)
    local tree = self:GetParent()
    local other = tree and tree.nodeCache and tree.nodeCache[otherEntryID]
    if not other or not other.entry then
        return false
    end
    local _, _, _, _, rank, maxRank, _, _, previewRank = GetTalentInfo(PET_TAB, other.entry.talentIndex, false, true, TalentGroup())
    local have = math.max(rank or 0, previewRank or 0)
    if self.entry.realParent == otherEntryID then
        return have >= (maxRank or 1)
    end
    return have > 0 and TreeInvestment() >= self.entry.RequiredInvestment
end

function PetNode:UpdateSearchMarker()
    self.Icon.LocationIcon:Hide()
end

function PetNode:OnClick(button)
    CloseDropDownMenus()
    if not self.entry then
        return
    end
    local index, group = self.entry.talentIndex, TalentGroup()
    if IsModifiedClick("CHATLINK") then
        local link = GetTalentLink(PET_TAB, index, false, true, group, true)
        if link and ChatEdit_InsertLink(link) then
            return
        end
    end
    if button == "RightButton" then
        if self.rank > self.learnedRank then
            AddPreviewTalentPoints(PET_TAB, index, -1, true, group)
            if self.deselectSound then PlaySound(self.deselectSound) end
        end
        return
    end
    if self.canLearn then
        AddPreviewTalentPoints(PET_TAB, index, 1, true, group)
        if self.selectSound then PlaySound(self.selectSound) end
    end
end

function PetNode:OnEnter()
    if not self.entry then
        return
    end
    GameTooltip:SetOwner(self, "ANCHOR_RIGHT")
    GameTooltip:SetTalent(PET_TAB, self.entry.talentIndex, false, true, TalentGroup(), true)
    if self.canLearn then
        GameTooltip_AddSpacer(GameTooltip)
        GameTooltip:AddLine(TOOLTIP_TALENT_LEARN, GREEN_FONT_COLOR:GetRGB())
    end
    if self.rank > self.learnedRank then
        GameTooltip:AddLine("Right-click: remove the pending point", DISABLED_FONT_COLOR:GetRGB())
    end
    if self.isGated then
        local r, g, b = RED_FONT_COLOR:GetRGB()
        GameTooltip:AddLine(TALENT_SPEND_MORE_POINTS, r, g, b, true)
    end
    GameTooltip:Show()
end

function PetNode:OnDragStart()
end

ShadowPetTalentButtonSquareMixin = CreateFromMixins(CoATalentButtonSquareMixin, PetNode)
ShadowPetTalentButtonSquareMixin.OnLoad = function(self)
    CoATalentButtonSquareMixin.OnLoad(self)
end

ShadowPetTalentButtonCircleMixin = CreateFromMixins(CoATalentButtonCircleMixin, PetNode)
ShadowPetTalentButtonCircleMixin.OnLoad = function(self)
    CoATalentButtonCircleMixin.OnLoad(self)
end

-------------------------------------------------------------------------------
-- Dados da arvore para o TalentTreeBase
-------------------------------------------------------------------------------
local entryCache = {}

local function BuildEntries()
    wipe(entryCache)
    local list, byCell = {}, {}
    local group = TalentGroup()
    local count = GetNumTalents(PET_TAB, false, true) or 0
    local n1 = { GetTalentInfo(PET_TAB, 1, false, true, group) }
    local n1g = { GetTalentInfo(PET_TAB, 1, false, true) }
    local tabName, _, spent, previewSpent = TabInfo()
    Log(format("BuildEntries grupo=%s numTabs=%s numTalents=%s aba=%s gasto=%s previa=%s livres=%s | talento1(grupo)=%s,%s,%s rank=%s/%s | talento1(sem grupo)=%s rank=%s",
        tostring(group), tostring(GetNumTalentTabs(false, true)), tostring(count), tostring(tabName), tostring(spent), tostring(previewSpent),
        tostring(GetUnspentTalentPoints(false, true, group)), tostring(n1[1]), tostring(n1[3]), tostring(n1[4]), tostring(n1[5]), tostring(n1[6]),
        tostring(n1g[1]), tostring(n1g[5])))
    for i = 1, count do
        local name, icon, tier, column, rank, maxRank, isExceptional = GetTalentInfo(PET_TAB, i, false, true, group)
        if name then
            local entry = {
                ID = ID_BASE + i,
                talentIndex = i,
                Name = name,
                Spells = {},
                ConnectedNodes = {},
                Group = 0,
                isExceptional = isExceptional,
                tier = tier,
                column = column,
                PositionX = (column - 1) * 2 + 1,       -- colunas 1-4 do pet -> 1, 3, 5, 7 da grade CoA
                PositionY = (tier - 1) * 1.8,            -- tiers 1-6 -> linhas 0 .. 9
                RequiredInvestment = (tier - 1) * PER_TIER,
            }
            list[#list + 1] = entry
            byCell[tier .. ":" .. column] = entry
            entryCache[entry.ID] = entry
        end
    end
    for _, entry in ipairs(list) do
        -- 3.3.5: GetTalentPrereqs devolve tier, column, isLearnable, isPetLearnable (os dois ultimos podem vir nil);
        -- talento de pet tem no maximo 1 pre-requisito, entao so tier e coluna importam
        local preTier, preColumn = GetTalentPrereqs(PET_TAB, entry.talentIndex, false, true, group)
        local parent = preTier and preColumn and byCell[preTier .. ":" .. preColumn]
        if parent then
            tinsert(entry.ConnectedNodes, parent.ID)
            entry.realParent = parent.ID
        end
    end
    -- arvore interligada como as do CoA: cada no sem pre-requisito liga aos nos da fileira de cima mais proxima
    -- (coluna ate 1 de distancia; se nao houver, ao mais perto). So visual: o servidor valida pelo tier.
    local tiers = {}
    for _, entry in ipairs(list) do
        tiers[entry.tier] = tiers[entry.tier] or {}
        tinsert(tiers[entry.tier], entry)
    end
    for _, entry in ipairs(list) do
        if not entry.realParent and entry.tier > 1 then
            local above
            for t = entry.tier - 1, 1, -1 do
                if tiers[t] then above = tiers[t] break end
            end
            if above then
                local near, best, bestDist = {}, nil, 99
                for _, other in ipairs(above) do
                    local d = math.abs(other.column - entry.column)
                    if d <= 1 then tinsert(near, other) end
                    if d < bestDist then best, bestDist = other, d end
                end
                if #near == 0 then near[1] = best end
                for _, other in ipairs(near) do
                    tinsert(entry.ConnectedNodes, other.ID)
                end
            end
        end
    end
    Log("BuildEntries -> " .. #list .. " entradas")
    return list
end

-------------------------------------------------------------------------------
-- Integracao com a janela N
-------------------------------------------------------------------------------
local Integration = {}

function Integration:CreateTree(treeView)
    local spec = treeView.SpecTree
    if self.tree then
        self.tree:Hide()
        self.tree.retired = true
    end
    local tree = CreateFrame("Frame", nil, treeView, "TalentTreeBase")
    tree:SetPoint("TOPRIGHT", treeView, "TOPRIGHT", -128, -110)
    tree:SetPoint("BOTTOMLEFT", treeView, "BOTTOM", 140, 40)
    tree:SetFrameLevel(spec:GetFrameLevel())
    tree.buttonWidth, tree.buttonHeight = 30, 30
    tree.buttonSpacingX, tree.buttonSpacingY = 14, 14
    tree.getEntries = function()
        local ok, list = pcall(BuildEntries)
        if not ok then Report(list) return {} end
        return list
    end
    tree.getEntry = function(id) return entryCache[id] end
    tree.getPosition = function(entry) return entry.PositionX, entry.PositionY end
    tree.getNodeTemplate = function(entry)
        return entry.isExceptional and "ShadowPetTalentButtonCircleTemplate" or "ShadowPetTalentButtonSquareTemplate"
    end
    tree.getChoiceNodeTemplate = function() return "CoATalentChoiceButtonTemplate" end
    tree.getConnectionTemplate = CoACharacterAdvancementUtil.GetDisplayTemplateForConnection
    tree.useGates = true
    tree.onlyOneGate = true
    tree.getGateTemplate = CoACharacterAdvancementUtil.GetDisplayTemplateForGate
    tree.getGateAttachmentPoint = CoACharacterAdvancementUtil.GetGateLeftAttachmentPoint
    tree.gateCurrencyCount = function() return TreeInvestment() end
    tree.getEntryGateRequirement = function(entry) return entry.RequiredInvestment end
    tree:Hide()

    tree.Label = tree:CreateFontString(nil, "OVERLAY", "GameFontHighlightHuge2")
    tree.Label:SetPoint("BOTTOM", tree, "TOP", 0, 70)
    tree.Points = tree:CreateFontString(nil, "OVERLAY", "GameFontHighlightHuge")
    tree.Points:SetPoint("TOP", tree.Label, "BOTTOM", 0, -2)

    tree.Learn = CreateFrame("Button", nil, tree, "UIPanelButtonTemplate")
    tree.Learn:SetSize(150, 24)
    tree.Learn:SetPoint("TOP", tree, "BOTTOM", -80, -6)
    tree.Learn:SetText("Learn Pet Talents")
    tree.Learn:SetScript("OnClick", function()
        LearnPreviewTalents(true)
    end)

    tree.Undo = CreateFrame("Button", nil, tree, "UIPanelButtonTemplate")
    tree.Undo:SetSize(110, 24)
    tree.Undo:SetPoint("LEFT", tree.Learn, "RIGHT", 8, 0)
    tree.Undo:SetText(UNDO or "Undo")
    tree.Undo:SetScript("OnClick", function()
        ResetGroupPreviewTalentPoints(true, TalentGroup())
    end)

    tree.Reset = CreateFrame("Button", nil, tree, "UIPanelButtonTemplate")
    tree.Reset:SetSize(150, 24)
    tree.Reset:SetPoint("BOTTOM", tree.Learn, "TOP", 0, 4)            -- acima do Learn, dentro da janela
    tree.Reset:SetText("Reset Pet Talents")
    tree.Reset:SetScript("OnClick", function()
        SendChatMessage(".petreset", "SAY")          -- o servidor responde no chat com o preco
        StaticPopup_Show("SHADOWCORE_PET_TALENT_RESET", UnitName("pet") or "")
    end)
    tree.Reset:SetScript("OnEnter", function(b)
        GameTooltip:SetOwner(b, "ANCHOR_RIGHT")
        GameTooltip:AddLine("Reset Pet Talents", 1, 1, 1)
        GameTooltip:AddLine("Refunds all of your pet's talent points for gold. The price is shown in chat.", NORMAL_FONT_COLOR:GetRGB())
        GameTooltip:AddLine("A Hunter trainer still resets them for free.", DISABLED_FONT_COLOR:GetRGB())
        GameTooltip:Show()
    end)
    tree.Reset:SetScript("OnLeave", GameTooltip_Hide)

    StaticPopupDialogs["SHADOWCORE_PET_TALENT_RESET"] = {
        text = "Reset all talents of %s? The gold price is shown in chat.",
        button1 = YES,
        button2 = NO,
        OnAccept = function() SendChatMessage(".petreset confirm", "SAY") end,
        timeout = 0,
        whileDead = 1,
        hideOnEscape = 1,
    }

    self.tree = tree
end

function Integration:CreateToggle(treeView)
    local button = CreateFrame("Button", "ShadowCorePetTalentToggle", treeView)
    button:SetSize(32, 32)
    button:SetPoint("TOPRIGHT", treeView.SpecTree.Points, "BOTTOM", -50, -6)
    button:SetFrameLevel(treeView.SpecTree:GetFrameLevel() + 10)

    button.Icon = button:CreateTexture(nil, "ARTWORK")
    button.Icon:SetPoint("CENTER")
    button.Icon:SetSize(24, 24)
    button.Icon:SetTexture("Interface\\Icons\\Ability_Hunter_BeastCall")
    button.Ring = button:CreateTexture(nil, "OVERLAY")
    button.Ring:SetAllPoints()
    button.Ring:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
    button.Ring:SetTexCoord(0, 0.6, 0, 0.6)
    button.Glow = button:CreateTexture(nil, "BACKGROUND")
    button.Glow:SetPoint("CENTER")
    button.Glow:SetSize(50, 50)
    button.Glow:SetTexture("Interface\\Buttons\\UI-ActionButton-Border")
    button.Glow:SetBlendMode("ADD")
    button.Count = button:CreateFontString(nil, "OVERLAY", "GameFontNormalOutline")
    button.Count:SetPoint("BOTTOMRIGHT", -2, 2)
    button:SetHighlightTexture("Interface\\Buttons\\ButtonHilight-Square", "ADD")

    button.Label = button:CreateFontString(nil, "OVERLAY", "GameFontNormal")
    button.Label:SetPoint("LEFT", button, "RIGHT", 8, 0)
    button.Label:SetText("Show Pet Talents")

    button:SetScript("OnClick", function()
        self.wantPet = not self.petMode
        self:SetPetMode(self.wantPet)
    end)
    button:SetScript("OnEnter", function(b)
        GameTooltip:SetOwner(b, "ANCHOR_RIGHT")
        GameTooltip:AddLine("Pet Talents", 1, 1, 1)
        local available = PointsAvailable()
        GameTooltip:AddLine(format("Unspent pet talent points: %d", available), NORMAL_FONT_COLOR:GetRGB())
        GameTooltip:AddLine(self.petMode and "Click to return to your specialization tree." or "Click to show your pet's talent tree.", GREEN_FONT_COLOR:GetRGB())
        GameTooltip:Show()
    end)
    button:SetScript("OnLeave", GameTooltip_Hide)
    button:Hide()
    self.toggle = button
end

function Integration:SetPetMode(enabled)
    Log("SetPetMode(" .. tostring(enabled) .. ") temArvore=" .. tostring(HasPetTree()))
    local treeView = self.treeView
    if enabled and not HasPetTree() then
        enabled = false
    end
    if not enabled and self.petMode then
        local _, preview = PointsAvailable()
        if preview > 0 then
            ResetGroupPreviewTalentPoints(true, TalentGroup())
        end
    end
    self.petMode = enabled
    treeView.SpecTree:SetShown(not enabled)
    if treeView.SpecTree.PassivesBackground then
        treeView.SpecTree.PassivesBackground:SetShown(not enabled)
    end
    if enabled then
        RequestSync()
        self:CreateTree(treeView)
        self.tree:Show()
        self:Rebuild()
        self:Watch()
    else
        self.tree:Hide()
    end
    self:UpdateToggle()
end

function Integration:State()
    local tree, visible = self.tree, 0
    if tree and type(tree.nodePool) == "table" then
        for node in tree.nodePool:EnumerateActive() do
            if node:IsVisible() then visible = visible + 1 end
        end
    end
    local w, h = 0, 0
    if tree then w, h = tree:GetWidth(), tree:GetHeight() end
    return format("modo pet=%s | arvore visivel=%s | nos visiveis=%d | talentos do pet=%d | tamanho=%dx%d | pet=%s | arvore=%s",
        tostring(self.petMode), tostring(tree and tree:IsVisible()), visible, GetNumTalents(PET_TAB, false, true) or 0,
        w or 0, h or 0, tostring(UnitName("pet")), tostring((TabInfo())))
end

function Integration:Watch()
    local elapsed = 0
    self.watcher = self.watcher or CreateFrame("Frame")
    self.watcher:SetScript("OnUpdate", function(f, dt)
        elapsed = elapsed + dt
        if elapsed < 1 then return end
        f:SetScript("OnUpdate", nil)
        Log("1s depois: " .. self:State())
        if self.petMode and not self:State():find("nos visiveis=[1-9]") then
            Report("a arvore abriu sem nos. " .. self:State())
        end
    end)
end

function Integration:Rebuild()
    if not self.petMode then
        return
    end
    local tabName = TabInfo()
    rebuildCount = rebuildCount + 1
    self.tree:SetClassTab(CLASS_KEY, (tabName or "Pet") .. ":" .. (UnitGUID("pet") or "none") .. ":" .. rebuildCount)
    self.tree:MarkDirty(TalentTreeBaseMixin.DirtyReason.RebuildTree)
    self:UpdatePoints()
end

function Integration:Refresh()
    if not self.petMode then
        self:UpdateToggle()
        return
    end
    self.tree:MarkDirty(TalentTreeBaseMixin.DirtyReason.Nodes)
    self:UpdatePoints()
end

function Integration:UpdatePoints()
    local tree = self.tree
    local tabName = TabInfo()
    tree.Label:SetText(format("PET: %s (%s)", (UnitName("pet") or "?"):upper(), (tabName or "?"):upper()))
    local available, preview = PointsAvailable()
    tree.Points:SetText(available)
    if available > 0 then
        tree.Points:SetTextColor(GREEN_FONT_COLOR:GetRGB())
    else
        tree.Points:SetTextColor(DISABLED_FONT_COLOR:GetRGB())
    end
    tree.Learn:SetEnabled(preview > 0)
    tree.Undo:SetEnabled(preview > 0)
    self:UpdateToggle()
end

function Integration:UpdateToggle()
    local show = HasPetTree()
    self.toggle:SetShown(show)
    if not show then
        if self.petMode then
            self:SetPetMode(false)
        end
        return
    end
    local available = PointsAvailable()
    self.toggle.Count:SetText(available > 0 and available or "")
    self.toggle.Glow:SetShown(available > 0 and not self.petMode)
    self.toggle.Icon:SetDesaturated(false)
    self.toggle.Label:SetText(self.petMode and "Show Spec Talents" or "Show Pet Talents")
end

function Integration:OnEvent(event, unit)
    if event ~= "UNIT_PET" or unit == "player" then Log("evento " .. event) end
    if event == "UNIT_PET" and unit ~= "player" then
        return
    end
    if not self.treeView:IsVisible() then
        return
    end
    if event == "UNIT_PET" and UnitExists("pet") and IsHunter() then
        RequestSync()
    end
    if event == "PET_TALENT_UPDATE" and self.petMode then
        self:Rebuild()
        return
    end
    if event == "UNIT_PET" or event == "PET_UI_UPDATE" then
        if self.petMode then
            self:Rebuild()
        end
        self:UpdateToggle()
    else
        self:Refresh()
    end
end

function Integration:Init()
    if self.ready or not IsHunter() then
        return
    end
    local frame = _G.CoATalentFrame
    local treeView = frame and frame.TreeView
    if not treeView or not treeView.SpecTree then
        return
    end
    self.ready = true
    self.treeView = treeView
    self:CreateTree(treeView)
    self:CreateToggle(treeView)

    local events = CreateFrame("Frame")
    for _, event in ipairs({ "UNIT_PET", "PET_UI_UPDATE", "PET_TALENT_UPDATE", "PREVIEW_PET_TALENT_POINTS_CHANGED",
        "PLAYER_TALENT_UPDATE", "CHARACTER_POINTS_CHANGED", "ASCENSION_CA_SPECIALIZATION_ACTIVE_ID_CHANGED" }) do
        pcall(events.RegisterEvent, events, event)
    end
    events:SetScript("OnEvent", function(_, event, ...) self:OnEvent(event, ...) end)

    treeView:HookScript("OnShow", function()
        self:UpdateToggle()
        if self.wantPet and HasPetTree() then
            self:SetPetMode(true)
        end
    end)
    treeView:HookScript("OnHide", function()
        local keep = self.wantPet
        self:SetPetMode(false)
        self.wantPet = keep
    end)
    if treeView:IsVisible() then
        self:UpdateToggle()
    end
end

ShadowCorePetTalents = Integration
SLASH_SHADOWCOREPET1 = "/spt"
SlashCmdList["SHADOWCOREPET"] = function() Report(Integration:State()) end
Integration:Init()
