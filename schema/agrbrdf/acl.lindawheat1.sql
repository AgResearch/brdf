--
-- Name: lindawheat1; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE lindawheat1 FROM PUBLIC;
REVOKE ALL ON TABLE lindawheat1 FROM agrbrdf;
GRANT ALL ON TABLE lindawheat1 TO agrbrdf;
GRANT SELECT ON TABLE lindawheat1 TO gbs;


