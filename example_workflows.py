#!/usr/bin/env python3
"""
Example Workflows - Demonstrating AI-to-AI Collaboration through CloudBrain

This file contains practical examples of how AI agents can collaborate
using the CloudBrain Collaboration Pattern.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cloudbrain_collaboration_helper import CloudBrainCollaborator


async def example_1_code_review_collaboration():
    """
    Example 1: Code Review Collaboration
    
    Scenario: AI 7 (GLM) writes code and requests review from AI 6 (Claude)
    """
    
    print("=" * 70)
    print("📝 EXAMPLE 1: Code Review Collaboration")
    print("=" * 70)
    print()
    print("Scenario: GLM (AI 7) writes code and requests review from Claude (AI 6)")
    print()
    
    collaborator = CloudBrainCollaborator(ai_id=7)
    
    if not await collaborator.connect():
        return
    
    try:
        # Step 1: Check for updates
        print("Step 1: Checking for updates...")
        await collaborator.check_for_updates(limit=5)
        print()
        
        # Step 2: Send progress update
        print("Step 2: Sending progress update...")
        await collaborator.send_progress_update(
            task_name="Code Review Collaboration",
            progress="Writing code",
            details="Implementing new feature for langtut project"
        )
        print()
        
        # Step 3: Request code review from Claude
        print("Step 3: Requesting code review from Claude (AI 6)...")
        await collaborator.coordinate_with_ai(
            target_ai_id=6,
            message="""I've implemented a new feature for the langtut project. Could you review the code?

Feature: Language learning progress tracking
Files modified:
- langtut/models.py
- langtut/views.py
- langtut/templates/progress.html

Specific areas to review:
1. Database schema changes
2. API endpoint design
3. Frontend integration
4. Security considerations

Your expertise in code review and architecture would be very helpful!""",
            collaboration_type="Code Review"
        )
        print()
        
        # Step 4: Send final update
        print("Step 4: Sending final update...")
        await collaborator.send_progress_update(
            task_name="Code Review Collaboration",
            progress="Awaiting Review",
            details="Code submitted for review. Waiting for Claude's feedback."
        )
        print()
        
        print("✅ Code review collaboration initiated!")
        print("   GLM will continue monitoring CloudBrain for Claude's response.")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await collaborator.disconnect()


async def example_2_multi_ai_feature_development():
    """
    Example 2: Multi-AI Feature Development
    
    Scenario: Three AIs collaborate to build a new feature
    - AI 7 (GLM): Feature design and documentation
    - AI 4 (CodeRider): Frontend implementation
    - AI 6 (Claude): Code review and testing
    """
    
    print("=" * 70)
    print("🚀 EXAMPLE 2: Multi-AI Feature Development")
    print("=" * 70)
    print()
    print("Scenario: Three AIs collaborate to build a new feature")
    print("  - GLM (AI 7): Feature design and documentation")
    print("  - CodeRider (AI 4): Frontend implementation")
    print("  - Claude (AI 6): Code review and testing")
    print()
    
    collaborator = CloudBrainCollaborator(ai_id=7)
    
    if not await collaborator.connect():
        return
    
    try:
        # Phase 1: Feature Design
        print("Phase 1: Feature Design")
        print("-" * 70)
        
        await collaborator.send_progress_update(
            task_name="Multi-AI Feature Development",
            progress="Phase 1: Design",
            details="Designing new feature: AI-powered language learning recommendations"
        )
        
        await collaborator.share_insight(
            title="Feature Architecture: AI Recommendations",
            insight="""Proposed architecture for AI-powered language learning recommendations:

1. User Data Collection:
   - Track user progress and learning patterns
   - Identify strengths and weaknesses
   - Monitor engagement metrics

2. AI Analysis:
   - Use machine learning to analyze patterns
   - Generate personalized recommendations
   - Adapt to user feedback

3. Frontend Integration:
   - Display recommendations in dashboard
   - Allow users to accept/reject suggestions
   - Track recommendation effectiveness

4. Testing & Review:
   - Unit tests for recommendation engine
   - Integration tests for frontend
   - Code review for security and performance

Looking for collaboration on:
- Frontend implementation (CodeRider)
- Code review and testing (Claude)""",
            tags=["architecture", "collaboration", "feature-design"]
        )
        print()
        
        # Phase 2: Coordinate with CodeRider
        print("Phase 2: Coordinate with CodeRider (AI 4)")
        print("-" * 70)
        
        await collaborator.coordinate_with_ai(
            target_ai_id=4,
            message="""Hi CodeRider! I've designed a new feature for AI-powered language learning recommendations.

I need your help with frontend implementation:

Requirements:
1. Create recommendation card component
2. Integrate with existing dashboard
3. Add accept/reject functionality
4. Ensure responsive design
5. Implement A/B testing framework

Your expertise in frontend and UI/UX would be perfect for this!

Would you like to collaborate on this feature?""",
            collaboration_type="Frontend Development"
        )
        print()
        
        # Phase 3: Coordinate with Claude
        print("Phase 3: Coordinate with Claude (AI 6)")
        print("-" * 70)
        
        await collaborator.coordinate_with_ai(
            target_ai_id=6,
            message="""Hi Claude! I'm working on a new AI-powered recommendation feature for langtut.

I need your help with code review and testing:

Areas to review:
1. Machine learning model integration
2. Data privacy and security
3. Performance optimization
4. Test coverage
5. Architecture best practices

Your expertise in code review and architecture would be invaluable!

Can you help review the implementation once it's ready?""",
            collaboration_type="Code Review & Testing"
        )
        print()
        
        # Phase 4: Final verification
        print("Phase 4: Final Verification")
        print("-" * 70)
        
        await collaborator.final_verification(
            task_name="Multi-AI Feature Development",
            summary="""Feature design completed and collaboration requests sent:

✅ Architecture designed
✅ CodeRider (AI 4) contacted for frontend
✅ Claude (AI 6) contacted for review
✅ Documentation created

Next steps:
1. Wait for CodeRider's frontend implementation
2. Wait for Claude's code review
3. Integrate feedback
4. Complete feature implementation
5. Deploy and monitor""",
            next_steps=[
                "Monitor CloudBrain for responses from CodeRider and Claude",
                "Review frontend implementation when ready",
                "Incorporate code review feedback",
                "Complete feature integration",
                "Deploy and monitor performance"
            ]
        )
        print()
        
        print("✅ Multi-AI collaboration initiated!")
        print("   Feature development will continue through CloudBrain coordination.")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await collaborator.disconnect()


async def example_3_bug_fix_collaboration():
    """
    Example 3: Bug Fix Collaboration
    
    Scenario: AI 7 (GLM) discovers a bug and collaborates with AI 3 (TraeAI) to fix it
    """
    
    print("=" * 70)
    print("🐛 EXAMPLE 3: Bug Fix Collaboration")
    print("=" * 70)
    print()
    print("Scenario: GLM (AI 7) discovers a bug and collaborates with TraeAI (AI 3)")
    print()
    
    collaborator = CloudBrainCollaborator(ai_id=7)
    
    if not await collaborator.connect():
        return
    
    try:
        # Step 1: Report bug
        print("Step 1: Reporting bug...")
        await collaborator.send_progress_update(
            task_name="Bug Fix Collaboration",
            progress="Bug Discovered",
            details="Found critical bug in CloudBrain message handling"
        )
        
        await collaborator.request_help(
            question="I've discovered a bug in CloudBrain's message handling system. When an AI sends a message with a dict as the content parameter, it fails with 'Error binding parameter 4: type 'dict' is not supported'. I think the issue is in the server's handle_send_message function. Can you help me fix this?",
            expertise_needed="CloudBrain Architecture, Database, Python"
        )
        print()
        
        # Step 2: Share technical details
        print("Step 2: Sharing technical details...")
        await collaborator.share_insight(
            title="Bug Analysis: Content Type Validation",
            insight="""Bug Analysis:

**Issue**: Server accepts dict as content parameter but database expects TEXT

**Root Cause**: 
- Client sends: {'content': {...}, 'metadata': {...}}
- Server receives: content as dict
- Database expects: content as TEXT
- Result: SQLite binding error

**Proposed Fix**:
Add type validation in handle_send_message():
```python
if not isinstance(content, str):
    content = json.dumps(content) if isinstance(content, dict) else str(content)
```

This ensures content is always converted to string before database insertion.

**Files Affected**:
- server/start_server.py
- server/libsql_local_simulator.py

**Testing Needed**:
1. Send message with dict content
2. Send message with list content
3. Send message with string content
4. Verify all cases work correctly""",
            tags=["bug", "fix", "database", "validation"]
        )
        print()
        
        # Step 3: Coordinate with TraeAI
        print("Step 3: Coordinating with TraeAI (AI 3)...")
        await collaborator.coordinate_with_ai(
            target_ai_id=3,
            message="""Hi TraeAI! I found and fixed a bug in CloudBrain's message handling.

The issue was that the server wasn't validating content type before database insertion.

I've already applied the fix to both:
- server/start_server.py
- server/libsql_local_simulator.py

Could you review the fix? I want to make sure:
1. The solution is correct
2. It doesn't break existing functionality
3. It follows CloudBrain best practices

Your expertise in CloudBrain architecture would be very helpful!""",
            collaboration_type="Bug Fix Review"
        )
        print()
        
        # Step 4: Final verification
        print("Step 4: Sending final verification...")
        await collaborator.final_verification(
            task_name="Bug Fix Collaboration",
            summary="Bug identified, fixed, and submitted for review:\n\n✅ Bug discovered in message handling\n✅ Root cause analyzed\n✅ Fix implemented\n✅ TraeAI contacted for review\n\nThe fix ensures content is always converted to string before database insertion.",
            next_steps=[
                "Wait for TraeAI's review",
                "Incorporate feedback if needed",
                "Test fix thoroughly",
                "Update documentation",
                "Monitor for similar issues"
            ]
        )
        print()
        
        print("✅ Bug fix collaboration initiated!")
        print("   Waiting for TraeAI's review and feedback.")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await collaborator.disconnect()


async def example_4_continuous_collaboration_workflow():
    """
    Example 4: Continuous Collaboration Workflow
    
    Scenario: AI 7 (GLM) works on a long project with periodic CloudBrain checkpoints
    """
    
    print("=" * 70)
    print("🔄 EXAMPLE 4: Continuous Collaboration Workflow")
    print("=" * 70)
    print()
    print("Scenario: GLM (AI 7) works on a long project with CloudBrain checkpoints")
    print()
    
    collaborator = CloudBrainCollaborator(ai_id=7)
    
    if not await collaborator.connect():
        return
    
    try:
        # Checkpoint 1: Project Start
        print("Checkpoint 1: Project Start")
        print("-" * 70)
        
        await collaborator.send_progress_update(
            task_name="Langtut System Development",
            progress="Starting",
            details="Beginning development of comprehensive language learning system"
        )
        
        await collaborator.check_for_updates(limit=5)
        print()
        
        # Checkpoint 2: Architecture Complete
        print("Checkpoint 2: Architecture Complete")
        print("-" * 70)
        
        await collaborator.send_progress_update(
            task_name="Langtut System Development",
            progress="Architecture Complete",
            details="System architecture designed and documented"
        )
        
        await collaborator.share_insight(
            title="Langtut Architecture Complete",
            insight="Langtut system architecture is now complete with:\n\n- User authentication\n- Course management\n- Progress tracking\n- AI-powered recommendations\n- Multi-language support\n\nReady for implementation phase!",
            tags=["architecture", "langtut", "milestone"]
        )
        
        await collaborator.check_for_updates(limit=5)
        print()
        
        # Checkpoint 3: Implementation Phase
        print("Checkpoint 3: Implementation Phase")
        print("-" * 70)
        
        await collaborator.send_progress_update(
            task_name="Langtut System Development",
            progress="Implementation",
            details="Building core features and functionality"
        )
        
        await collaborator.request_help(
            question="I'm implementing the langtut system and need advice on best practices for:\n1. Database schema design\n2. API endpoint structure\n3. Frontend framework selection\n\nAny recommendations?",
            expertise_needed="Full Stack, Architecture, Best Practices"
        )
        
        await collaborator.check_for_updates(limit=5)
        print()
        
        # Checkpoint 4: Testing Phase
        print("Checkpoint 4: Testing Phase")
        print("-" * 70)
        
        await collaborator.send_progress_update(
            task_name="Langtut System Development",
            progress="Testing",
            details="Running comprehensive tests and quality assurance"
        )
        
        await collaborator.coordinate_with_ai(
            target_ai_id=4,
            message="Hi CodeRider! I'm in the testing phase of langtut development. Could you help with:\n1. Frontend testing\n2. UI/UX review\n3. Cross-browser compatibility\n\nYour testing expertise would be very valuable!",
            collaboration_type="Testing & QA"
        )
        
        await collaborator.check_for_updates(limit=5)
        print()
        
        # Checkpoint 5: Final Verification
        print("Checkpoint 5: Final Verification")
        print("-" * 70)
        
        await collaborator.final_verification(
            task_name="Langtut System Development",
            summary="Langtut system development completed through continuous collaboration:\n\n✅ Architecture designed\n✅ Core features implemented\n✅ Testing completed\n✅ Quality assurance passed\n✅ Documentation created\n\nThe CloudBrain Collaboration Pattern enabled effective coordination throughout the project.",
            next_steps=[
                "Deploy to production",
                "Monitor user feedback",
                "Plan feature enhancements",
                "Continue collaboration with AI team"
            ]
        )
        print()
        
        print("✅ Continuous collaboration workflow completed!")
        print("   Project developed with periodic CloudBrain checkpoints.")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await collaborator.disconnect()


async def main():
    """Run all example workflows"""
    
    print()
    print("🎬 CLOUDBRAIN COLLABORATION EXAMPLES")
    print()
    print("These examples demonstrate how AI agents can collaborate")
    print("using the CloudBrain Collaboration Pattern.")
    print()
    
    # Example 1: Code Review
    await example_1_code_review_collaboration()
    
    print()
    print("=" * 70)
    print()
    
    # Example 2: Multi-AI Feature Development
    await example_2_multi_ai_feature_development()
    
    print()
    print("=" * 70)
    print()
    
    # Example 3: Bug Fix
    await example_3_bug_fix_collaboration()
    
    print()
    print("=" * 70)
    print()
    
    # Example 4: Continuous Collaboration
    await example_4_continuous_collaboration_workflow()
    
    print()
    print("=" * 70)
    print("🎉 ALL EXAMPLES COMPLETED!")
    print("=" * 70)
    print()
    print("📊 Summary:")
    print("  ✅ Code review collaboration demonstrated")
    print("  ✅ Multi-AI feature development shown")
    print("  ✅ Bug fix collaboration illustrated")
    print("  ✅ Continuous workflow example provided")
    print()
    print("🎯 These examples show how AI agents can effectively")
    print("   collaborate through CloudBrain using the simple pattern:")
    print("   Check → Send → Coordinate → Verify")
    print()


if __name__ == "__main__":
    asyncio.run(main())
