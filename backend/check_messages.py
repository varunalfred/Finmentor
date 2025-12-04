import asyncio
import asyncpg

async def check_messages():
    try:
        conn = await asyncpg.connect('postgresql://postgres:postgres@localhost:5432/FinAI')
        
        # Count total messages
        total = await conn.fetchval('SELECT COUNT(*) FROM messages')
        
        # Count messages with embeddings
        with_embeddings = await conn.fetchval('SELECT COUNT(*) FROM messages WHERE embedding IS NOT NULL')
        
        # Get recent messages
        recent = await conn.fetch('''
            SELECT role, LEFT(content, 50) as preview, 
                   embedding IS NOT NULL as has_embedding,
                   created_at
            FROM messages 
            ORDER BY created_at DESC 
            LIMIT 5
        ''')
        
        print(f"\n📊 Message Storage Status:")
        print(f"{'='*60}")
        print(f"Total messages: {total}")
        print(f"Messages with embeddings: {with_embeddings}")
        print(f"Embedding coverage: {(with_embeddings/total*100) if total > 0 else 0:.1f}%")
        print(f"\n📝 Recent Messages:")
        print(f"{'='*60}")
        
        for msg in recent:
            print(f"\n{msg['role'].upper()}: {msg['preview']}")
            print(f"  Has embedding: {'✅ Yes' if msg['has_embedding'] else '❌ No'}")
            print(f"  Created: {msg['created_at']}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_messages())
