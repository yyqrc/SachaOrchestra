using UnityEngine;

internal static class EnglishRuntimeLog
{
    internal static void ReportExportSize(int size)
    {
        Debug.Log($"Material export size: {size}");
    }
}
