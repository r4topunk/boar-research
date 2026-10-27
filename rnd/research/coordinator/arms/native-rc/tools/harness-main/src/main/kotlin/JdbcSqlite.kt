package team.sopa.boar.engine.db

import java.sql.Connection
import java.sql.DriverManager
import java.sql.ResultSet

/** [SqlDatabase] over sqlite-jdbc (a real SQLite with FTS5), for JVM tests of the engine's SQL. */
class JdbcSqlite(path: String = ":memory:") : SqlDatabase {
    private val conn: Connection = DriverManager.getConnection("jdbc:sqlite:$path")
    private var txDepth = 0

    override fun <T> query(sql: String, args: List<Any?>, map: (SqlRow) -> T): List<T> =
        conn.prepareStatement(sql).use { st ->
            args.forEachIndexed { i, v -> st.setObject(i + 1, if (v is Boolean) (if (v) 1 else 0) else v) }
            st.executeQuery().use { rs ->
                val row = Row(rs)
                val out = ArrayList<T>()
                while (rs.next()) out += map(row)
                out
            }
        }

    override fun execute(sql: String, args: List<Any?>): Long = conn.prepareStatement(sql).use { st ->
        args.forEachIndexed { i, v -> st.setObject(i + 1, if (v is Boolean) (if (v) 1 else 0) else v) }
        st.executeUpdate().toLong()
    }

    override fun exec(script: String) { conn.createStatement().use { it.executeUpdate(script) } }

    override fun lastInsertRowid(): Long = query("SELECT last_insert_rowid()") { it.long(0) }.first()

    override fun <T> transaction(block: () -> T): T {
        if (txDepth > 0) return block()
        conn.autoCommit = false
        txDepth++
        try {
            val r = block()
            conn.commit()
            return r
        } catch (e: Throwable) {
            conn.rollback()
            throw e
        } finally {
            txDepth--
            conn.autoCommit = true
        }
    }

    override fun close() = conn.close()

    private class Row(private val rs: ResultSet) : SqlRow {
        override val columnCount: Int get() = rs.metaData.columnCount
        override fun columnName(i: Int): String = rs.metaData.getColumnLabel(i + 1)
        override fun isNull(i: Int): Boolean { rs.getObject(i + 1); return rs.wasNull() }
        override fun long(i: Int): Long = rs.getLong(i + 1)
        override fun double(i: Int): Double = rs.getDouble(i + 1)
        override fun string(i: Int): String? = rs.getString(i + 1)
        override fun blob(i: Int): ByteArray? = rs.getBytes(i + 1)
    }
}

/** zstd through zstd-jni, for tests. */
val jvmZstd = Zstd { src -> com.github.luben.zstd.ZstdInputStream(src.inputStream()).readBytes() }
