--[[
    SimpleMageRotation - Basic Mage Rotation Addon
    Version: 1.0
    
    This is a SIMPLE, COMPLIANT addon that provides:
    - Manual toggle rotation on/off
    - Basic spell rotation when enabled
    - Visual feedback on rotation state
    
    IMPORTANT: This does NOT automatically target, loot, or move.
    It only casts spells when YOU have a target selected.
    
    Commands:
    /smr - Toggle rotation
    /smr on - Enable rotation
    /smr off - Disable rotation
    /smr status - Show current status
]]

SimpleMageRotation = {
    name = "SimpleMageRotation",
    version = "1.0",
    enabled = false,
    lastCastTime = 0,
    castDelay = 2.0,  -- Delay between spell casts (seconds)
}

-- Configuration (can be modified)
local config = {
    -- Spell key bindings (modify to match your keys)
    attackKey = "1",      -- Auto attack / wand
    spell1Key = "2",      -- Primary damage spell (Fireball)
    spell2Key = "3",      -- Secondary spell (Frostbolt)
    aoeSpellKey = "4",    -- AOE spell (Blizzard)
    foodKey = "5",
    drinkKey = "6",
    
    -- Thresholds
    eatThreshold = 70,    -- Eat when HP below this %
    drinkThreshold = 40, -- Drink when mana below this %
    
    -- Combat settings
    autoEat = true,
    autoDrink = true,
    enableAOE = false,    -- AOE disabled by default
    aoeThreshold = 3,     -- Enemies needed for AOE
}

-- Local variables
local lastEatTime = 0
local lastDrinkTime = 0

-- ============================================
-- Utility Functions
-- ============================================

local function GetSpellRank(name)
    for i = 1, 100 do
        local spellName = GetSpellName(i, "spell")
        if spellName and spellName == name then
            return i
        end
    end
    return nil
end

local function CastSpellSafe(name)
    local rank = GetSpellRank(name)
    if not rank then return false end
    
    -- Check if we have enough mana (rough estimate)
    local mana = UnitMana("player")
    local manaCost = 0
    
    -- Simple mana cost table (approximate)
    local costs = {
        ["火球术"] = 65,
        ["寒冰箭"] = 45,
        ["暴风雪"] = 160,
        ["奥术爆炸"] = 35,
        ["魔爆术"] = 40,
    }
    
    manaCost = costs[name] or 50
    
    if mana < manaCost then
        return false
    end
    
    -- Check cooldown
    local start, duration = GetSpellCooldown(rank, "spell")
    if start > 0 then
        return false
    end
    
    CastSpell(rank, "spell")
    return true
end

local function HasTarget()
    return UnitExists("target") and not UnitIsDead("target") and UnitCanAttack("player", "target")
end

local function IsInCombat()
    return UnitAffectingCombat("player")
end

-- ============================================
-- Core Functions
-- ============================================

local function DoRotation()
    if not SimpleMageRotation.enabled then return false end
    if not HasTarget() then return false end
    if not IsInCombat() then return false end
    
    local now = GetTime()
    if now - SimpleMageRotation.lastCastTime < SimpleMageRotation.castDelay then
        return false
    end
    
    -- Try to cast spells based on available mana
    local mana = UnitMana("player")
    local manaPercent = (mana / UnitManaMax("player")) * 100
    
    -- Determine spell to cast
    local spellToCast = nil
    
    if config.enableAOE then
        -- AOE mode - try blizzard first if we have enough mana
        if mana >= 160 then
            spellToCast = "暴风雪"
        elseif mana >= 35 and manaPercent > 30 then
            spellToCast = "魔爆术"
        end
    end
    
    -- Single target mode
    if not spellToCast then
        if mana >= 65 and manaPercent > 30 then
            spellToCast = "火球术"
        elseif mana >= 45 then
            spellToCast = "寒冰箭"
        end
    end
    
    -- Cast the spell
    if spellToCast and CastSpellSafe(spellToCast) then
        SimpleMageRotation.lastCastTime = now
        return true
    end
    
    -- Fallback to attack/wand
    CastSpellSafe("攻击")
    return true
end

local function CheckConsumables()
    if not SimpleMageRotation.enabled then return end
    
    local now = GetTime()
    
    -- Check eating
    if config.autoEat then
        local hp = UnitHealth("player")
        local maxHp = UnitHealthMax("player")
        local hpPercent = (hp / maxHp) * 100
        
        if hpPercent < config.eatThreshold and now - lastEatTime > 3 then
            -- Try to use food (this assumes you have food bound to a key)
            -- You'll need to bind food in-game and this will press that key
            CastSpellByName(config.foodKey)
            lastEatTime = now
        end
    end
    
    -- Check drinking
    if config.autoDrink then
        local mana = UnitMana("player")
        local maxMana = UnitManaMax("player")
        local manaPercent = (mana / maxMana) * 100
        
        if manaPercent < config.drinkThreshold and now - lastDrinkTime > 3 then
            CastSpellByName(config.drinkKey)
            lastDrinkTime = now
        end
    end
end

-- ============================================
-- Event Handlers
-- ============================================

function SimpleMageRotation:OnLoad()
    -- Register events
    self:RegisterEvent("PLAYER_REGEN_ENABLED")      -- Exiting combat
    self:RegisterEvent("PLAYER_REGEN_DISABLED")     -- Entering combat
    self:RegisterEvent("UNIT_HEALTH")
    self:RegisterEvent("UNIT_MANA")
    
    -- Register slash commands
    SLASH_SMR1 = "/smr"
    SLASH_SMR2 = "/simplemagerotation"
    SlashCmdList["SMR"] = function(msg)
        self:HandleCommand(msg)
    end
    
    -- Print welcome message
    DEFAULT_CHAT_FRAME:AddMessage("|cff66cceeSimpleMageRotation|r v" .. self.version .. " loaded")
    DEFAULT_CHAT_FRAME:AddMessage("Use |cffFFFF00/smr on|r or |cffFFFF00/smr off|r to toggle rotation")
end

function SimpleMageRotation:OnEvent(event, ...)
    if event == "PLAYER_REGEN_ENABLED" then
        -- Exited combat - reset state
    elseif event == "PLAYER_REGEN_DISABLED" then
        -- Entered combat
    elseif event == "UNIT_HEALTH" then
        -- Health changed
    elseif event == "UNIT_MANA" then
        -- Mana changed
    end
end

function SimpleMageRotation:OnUpdate(delta)
    if not self.enabled then return end
    if not HasTarget() then return end
    
    -- Do rotation if in combat
    if IsInCombat() then
        DoRotation()
    end
    
    -- Check consumables
    CheckConsumables()
end

function SimpleMageRotation:HandleCommand(msg)
    if not msg or msg == "" or msg == "status" then
        local status = self.enabled and "|cff00FF00Enabled|r" or "|cffff0000Disabled|r"
        DEFAULT_CHAT_FRAME:AddMessage("SimpleMageRotation Status: " .. status)
        DEFAULT_CHAT_FRAME:AddMessage("Rotation: " .. status)
        DEFAULT_CHAT_FRAME:AddMessage("AOE: " .. (config.enableAOE and "|cff00FF00Enabled|r" or "|cffff0000Disabled|r"))
    elseif msg == "on" then
        self.enabled = true
        DEFAULT_CHAT_FRAME:AddMessage("|cff66cceeSimpleMageRotation|r |cff00FF00Enabled|r")
    elseif msg == "off" then
        self.enabled = false
        DEFAULT_CHAT_FRAME:AddMessage("|cff66cceeSimpleMageRotation|r |cffff0000Disabled|r")
    elseif msg == "aoe on" then
        config.enableAOE = true
        DEFAULT_CHAT_FRAME:AddMessage("|cff66cceeSimpleMageRotation|r AOE |cff00FF00Enabled|r")
    elseif msg == "aoe off" then
        config.enableAOE = false
        DEFAULT_CHAT_FRAME:AddMessage("|cff66cceeSimpleMageRotation|r AOE |cffff0000Disabled|r")
    elseif msg == "test" then
        -- Test cast
        if CastSpellSafe("火球术") then
            DEFAULT_CHAT_FRAME:AddMessage("Test cast successful")
        else
            DEFAULT_CHAT_FRAME:AddMessage("Test cast failed - check spell/mana/cooldown")
        end
    else
        DEFAULT_CHAT_FRAME:AddMessage("|cff66cceeSimpleMageRotation|r Commands:")
        DEFAULT_CHAT_FRAME:AddMessage("/smr on - Enable rotation")
        DEFAULT_CHAT_FRAME:AddMessage("/smr off - Disable rotation")
        DEFAULT_CHAT_FRAME:AddMessage("/smr aoe on - Enable AOE")
        DEFAULT_CHAT_FRAME:AddMessage("/smr aoe off - Disable AOE")
        DEFAULT_CHAT_FRAME:AddMessage("/smr status - Show status")
    end
end

-- ============================================
-- Key Bindings (Optional)
-- ============================================

-- You can bind keys in game to these functions
function SimpleMageRotation_ToggleRotation()
    SimpleMageRotation.enabled = not SimpleMageRotation.enabled
    local status = SimpleMageRotation.enabled and "Enabled" or "Disabled"
    DEFAULT_CHAT_FRAME:AddMessage("SimpleMageRotation " .. status)
end
