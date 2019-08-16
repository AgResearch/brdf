--
-- Name: datasourcelist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE datasourcelist FROM PUBLIC;
REVOKE ALL ON TABLE datasourcelist FROM agrbrdf;
GRANT ALL ON TABLE datasourcelist TO agrbrdf;
GRANT SELECT ON TABLE datasourcelist TO gbs;


