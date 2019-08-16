--
-- Name: op; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE op FROM PUBLIC;
REVOKE ALL ON TABLE op FROM agrbrdf;
GRANT ALL ON TABLE op TO agrbrdf;
GRANT SELECT ON TABLE op TO gbs;


