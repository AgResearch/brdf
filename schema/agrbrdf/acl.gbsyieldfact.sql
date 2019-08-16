--
-- Name: gbsyieldfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE gbsyieldfact FROM PUBLIC;
REVOKE ALL ON TABLE gbsyieldfact FROM agrbrdf;
GRANT ALL ON TABLE gbsyieldfact TO agrbrdf;
GRANT SELECT ON TABLE gbsyieldfact TO gbs;


