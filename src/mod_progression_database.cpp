#include "BuiltInConfig.h"
#include "Config.h"
#include "DBUpdater.h"
#include "Log.h"

#include "mod_progression.h"

#include <array>
#include <filesystem>
#include <string>
#include <vector>

namespace
{
constexpr std::array<char const*, PATCH_MAX> PatchDirectories =
{
    "patch_00-1_1",
    "patch_01-1_2",
    "patch_02-1_3",
    "patch_03-1_4",
    "patch_04-1_5",
    "patch_05-1_6",
    "patch_06-1_7",
    "patch_07-1_8",
    "patch_08-1_9",
    "patch_09-1_10",
    "patch_10-1_11",
    "patch_11-1_12",
    "patch_12-2_0",
    "patch_13-2_1",
    "patch_14-2_2",
    "patch_15-2_3",
    "patch_16-2_4",
    "patch_17-3_0",
    "patch_18-3_1",
    "patch_19-3_2",
    "patch_20-3_3",
    "patch_21-3_3_5"
};

std::string ResolveProgressionSourcePath()
{
    namespace fs = std::filesystem;

    fs::path const sourceDirectory(BuiltInConfig::GetSourceDirectory());

    std::vector<std::string> candidates;
    std::string configuredDirectory = sConfigMgr->GetOption<std::string>("Progression.ModuleDirectory", "");
    if (!configuredDirectory.empty())
        candidates.push_back(configuredDirectory);

    candidates.emplace_back("mod-azeroth-eras");
    candidates.emplace_back("mod-02-progression");
    candidates.emplace_back("mod-progression");

    for (std::string const& directory : candidates)
    {
        fs::path moduleSource = sourceDirectory / "modules" / directory / "src";
        std::error_code error;
        if (fs::is_directory(moduleSource, error))
        {
            LOG_INFO("server.loading", "Progression: using SQL source directory modules/{}/src", directory);
            return "/modules/" + directory + "/src/";
        }
    }

    LOG_ERROR("server.loading",
        "Progression: could not find the module source directory. Checked mod-azeroth-eras, mod-02-progression, and mod-progression under {}. Set Progression.ModuleDirectory if the module uses another folder name.",
        sourceDirectory.generic_string());

    return {};
}
}

void Progression::OnAfterDatabasesLoaded(uint32 updateFlags)
{
    if (!DBUpdater<WorldDatabaseConnection>::IsEnabled(updateFlags))
        return;

    std::vector<std::string> patchDatabaseDirectories = GetActivePatches();
    if (patchDatabaseDirectories.empty())
    {
        LOG_ERROR("server.loading", "Progression: no patch SQL directories were found; progression database updates were not applied.");
        return;
    }

    if (sConfigMgr->GetOption<bool>("Progression.Reset", false))
    {
        if (!sConfigMgr->GetOption<bool>("Progression.Development.AllowUnsafeReset", false))
        {
            LOG_ERROR("server.loading",
                "Progression: reset was requested but blocked. Progression.Reset only replays cumulative SQL and is not a rollback. Use a disposable database and explicitly set Progression.Development.AllowUnsafeReset = 1 to allow it.");
        }
        else
        {
            LOG_INFO("server.loading", "Progression: unsafe development reset requested; clearing previously applied patch_* update records.");
            WorldDatabase.Query("DELETE FROM `updates` WHERE `name` LIKE 'patch_%'");
        }
    }

    DBUpdater<WorldDatabaseConnection>::Update(WorldDatabase, &patchDatabaseDirectories);
}

std::vector<std::string> Progression::GetActivePatches()
{
    namespace fs = std::filesystem;

    std::vector<std::string> activePatches;
    std::string pathToPatches = ResolveProgressionSourcePath();
    if (pathToPatches.empty())
        return activePatches;

    uint8 patchId = sConfigMgr->GetOption<uint8>("Progression.Patch", DEFAULT_PROGRESSION_PATCH);
    if (patchId >= PATCH_MAX)
    {
        LOG_ERROR("server.loading", "Progression: patch id {} is invalid; falling back to patch 1.0 (id {}).", patchId, DEFAULT_PROGRESSION_PATCH);
        patchId = DEFAULT_PROGRESSION_PATCH;
    }

    fs::path const sourceDirectory(BuiltInConfig::GetSourceDirectory());

    for (uint8 i = PATCH_WORLD_OF_WARCRAFT; i <= patchId; ++i)
    {
        std::string relativeDirectory = pathToPatches + PatchDirectories[i] + "/sql";
        fs::path absoluteDirectory(sourceDirectory.generic_string() + relativeDirectory);

        std::error_code error;
        if (!fs::is_directory(absoluteDirectory, error))
        {
            LOG_ERROR("server.loading", "Progression: missing patch SQL directory: {}", absoluteDirectory.generic_string());
            continue;
        }

        activePatches.push_back(relativeDirectory);
    }

    LOG_INFO("server.loading", "Progression: patch {} selected; {} cumulative patch SQL director{} queued.",
        patchId, activePatches.size(), activePatches.size() == 1 ? "y" : "ies");

    return activePatches;
}
